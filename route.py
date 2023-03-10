# Semantic Changes:
# Add popup to signify non login
# Add info (i) button to explain what the sections in the create project page require
# Add info (i) button for status questionnare skill explanation
# Change menu buttons to icons, with hover showing text eg Create Project, Update Status, Log Out etc.
# Make skill slider equal in length, currently start at different paddings
# Add stats to Dev home page?
from trackGit import get_24_hour_issues_count, get_7_day_issues_count, get_hourly_commits
from werkzeug import security
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import json
from concrete import *
import numpy as np
from datetime import date, timedelta
import sys
# sys.tracebacklimit = 0

app = Flask(__name__)
app.secret_key = 'SecRetKeyHighLyConFiDENtIal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RiskTracker.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from schema import db, User, DeveloperStrength, UserSkills, dbinit, RiskComponent, Projects, DeveloperProject, ProjectRisk
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# change this to False to avoid resetting the database every time this app is restarted
resetdb = False
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()

def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def softSkillRisk(proj_id):
    #Get all Developers on the project
    # Calculate the average soft skill for the project
    # Calculate Expected soft skill based on team size
    # Calculate percentage difference from expected
    skillSumCount = 0
    currentProject = ProjectsClass(proj_id)
    teamCount = len(currentProject.team)
    for member in currentProject.team:
        skillRow = UserSkills.query.filter_by(user_id=member).first()
        skillSumCount += skillRow.enthusiasm + skillRow.purpose + skillRow.challenge + skillRow.health + skillRow.resilience
    # print("Skill Sum Count")
    # print('-----------------')
    # print(skillSumCount)
    # maxSkillCount = teamCount * 5 * 5
    avgSkill = teamCount * 5 * 3
    if(skillSumCount == 0):
        return 1
    return avgSkill/skillSumCount

def teamMemberRisk(proj_id):
    currentProject = ProjectsClass(proj_id)
    # totalTogether = 0
    totalSuccessful = 0
    totalFailed = 0
    for member in currentProject.team:
        projects = DeveloperProject.query.filter_by(developer_id=member).all()
        for project in projects:
            team = DeveloperProject.query.with_entities(DeveloperProject.developer_id).filter_by(project_id=project.project_id).all()
            team = [r[0] for r in team]
            # print("Team", team)
            # print("Current Project Team: ", currentProject.team)
            count = len(set(currentProject.team) & set(team))
            count = count - 1
            # totalTogether += count
            resProject = Projects.query.filter_by(project_id=project.project_id).first()
            if resProject == "Completed":
                totalSuccessful += count
            if resProject == "Failed":
                totalFailed += count
            # print("Member: ", member)
            # print("Count: ", count)
    performance = 1 + ( (totalFailed) * 0.5 - totalSuccessful * 0.125)
    if performance < 0.01:
        performance = 0.1
    # print("Total Together: ", performance)
    return performance

def monte_carlo(simulations, deadline, project):
    monteCarlo = list()

    for i in range(len(project)):
        iStd = np.std(project[i])
        iMean = np.mean(project[i])
        runs = np.random.normal(iMean,iStd,simulations)
        

        monteCarlo.append(runs.tolist())
    if not monteCarlo:
        #Chance of success of an average project from the problem statement
        return 34
    # print("MONTE CARLO: ", monteCarlo[0])
    estimates = list()
    for i in range(len(monteCarlo[0])):
        daysSum = 0
        for j in range(len(monteCarlo)):
            daysSum += monteCarlo[j][i]
        estimates.append(daysSum)

    # print("ESTIMATES: ", estimates)

    successCount = 0
    for estimate in estimates:
        if estimate <= deadline:
            successCount += 1

    successPercentage = (successCount/simulations) * 100

    return successPercentage

def githubIssues(repo, owner):
    yesterday = date.today() - timedelta(days=1)
    oneWeekAgo = yesterday - timedelta(days=7)
    print(yesterday)
    print(oneWeekAgo)
    twenty_four_hour_issues = get_24_hour_issues_count(repo, owner, yesterday)
    seven_day_issues = get_7_day_issues_count(repo, owner, oneWeekAgo)
    seven_day_issues = seven_day_issues/7
    print("24 Hour Issues: ", twenty_four_hour_issues)
    print("7 Day Issues: ", seven_day_issues)
    if twenty_four_hour_issues == 0 and seven_day_issues <= 1:
        return 1
    elif twenty_four_hour_issues == 0 and seven_day_issues > 1:
        #1 s.d. below the mean
        return 0.5
    return (twenty_four_hour_issues/seven_day_issues)

def hourlyCommits(repo, owner):
    hourly_commits = get_hourly_commits(repo, owner)
    print("Hourly Commits: ", hourly_commits)
    potential_error_commits = 0
    # https://www.bu.edu/ballab/pubs/Riley_2017.pdf
    for i in range(6):
        potential_error_commits += hourly_commits[i]
    for i in range(23, 24):
        potential_error_commits += hourly_commits[i]
    print("Potential Error Commits: ", potential_error_commits)
    print("Hourly Commits: ", hourly_commits.sum())
    if hourly_commits.sum() == 0:
        return 1
    potential_error_commit_likelihood = (potential_error_commits/hourly_commits.sum())
    print("Potential Error Commits: ", potential_error_commit_likelihood)
    # https://redbooth.com/blog/your-most-productive-time
    if potential_error_commit_likelihood <= 0.07:
        return 1
    else: potential_error_commit_likelihood = 1 + (potential_error_commit_likelihood - 0.07)
    return potential_error_commit_likelihood

def member_skills(proj_id):
    currentProject = ProjectsClass(proj_id)
    for member in currentProject.team:
        strengths = DeveloperStrength.query.with_entities(DeveloperStrength.strength).filter_by(developer_id=member).all()
        print(strengths)


def calculateRisk(proj_id):
    # Sources of primary risk multipliers
    # 1. Team member risk (1.XX)
    # 2. Hourly commits (0.XX)
    # 3. Github issues (0.XX)
    # 4. Monte Carlo Cost (0.XX)
    # 5. Monte Carlo Time (0.XX)
    # 6. Member Skills
    gitRisk = githubIssues("calculator","microsoft")
    member_skills(4)
    proj_manager_id = proj_id
    project = Projects.query.filter_by(project_id=proj_id).first()
    rcList = list()
    rcRowList = list()

    tcList = list()
    tcRowList = list()
    assignedBudget = project.budget
    print("Assigned Budget: ", assignedBudget)
    assignedDeadline = project.deadline
    print("Assigned Deadline: ", assignedDeadline)

    simulations = 10000
    risk = ProjectRisk.query.filter_by(project_id = proj_id).first()
    #Thread open
    costComponents = RiskComponent.query.filter_by(project_risk_id = risk.project_risk_id, risk_type = "Cost").all()
    print("Cost Components: ", costComponents)
    for component in costComponents:
        rcRowList.append(component.best)
        rcRowList.append(component.worst)
        rcRowList.append(component.average)
        print("RC Row List: ", rcRowList)
        rcList.append(rcRowList)
        rcRowList = list()
    print("RC List: ", rcList)
    costMC = monte_carlo(simulations, assignedBudget, rcList)
    timeComponents = RiskComponent.query.filter_by(project_risk_id = risk.project_risk_id, risk_type = "Time").all()

    
    for rComponent in timeComponents:
        tcRowList.append(rComponent.best)
        tcRowList.append(rComponent.worst)
        tcRowList.append(rComponent.average)
        tcList.append(rcRowList)
        tcRowList.clear()
    print("TC List: ", tcList)
    timeMC = monte_carlo(simulations, assignedDeadline, tcList)

    #finalMC gives the risk multiplier
    finalMC = ((34/costMC) + (34/timeMC))/2
    #Thread close
    print("Cost MC: ", costMC)
    print("Time MC: ", timeMC)

    print("Final MC: ", finalMC)

    memberRisk = teamMemberRisk(proj_id)
    softSkillRiskMultiplier = softSkillRisk(proj_id)
    hourly_commits = hourlyCommits('calculator', 'microsoft')
    currentRisk = ProjectRisk.query.filter_by(project_id = proj_id).first()
    #currentRisk.project_risk_value
    #Developer Skills
    print("Member Risk: ", memberRisk)
    print("Soft Skill Risk Multiplier: ", softSkillRiskMultiplier)
    print("Hourly Commits: ", hourly_commits)
    print("Final MC: ", finalMC)
    print("Git Risk: ", gitRisk)
    risky_business = 1 * memberRisk * hourly_commits * gitRisk * finalMC * softSkillRiskMultiplier
    print()
    print("Risky Business: ", risky_business)
    return risky_business


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# RENDER_TEMPLATES =============================================================================================================
# login page
@app.route('/')
def index():
    return render_template('/login.html')

# register new user
@app.route('/register')
def reg():
    return render_template('/register.html')

# developer homepage
@app.route('/developerHome')
def developerHome():
    if 'user' not in session:
        return redirect('/')
    
    # user = Developer(session['user']['email'])
    userProjects = Developer.createUserProjects(session['currentProjects'])

    currentProjects = []
    for project in userProjects:
        currentProjects.append(as_dict(project))

    print(session['currentProjects'])
    print(currentProjects)

    return render_template('/developerHome.html', name=session['user']['first_name'],projects=currentProjects)

# developer strengths
@app.route('/developerSkills')
def developerSkills():
    return render_template('/developerSkills.html', currentSkills=session['strengths'])

# user soft skills
@app.route('/softSkills', methods = ['GET', 'POST'])
def softSkills():
    if 'user' not in session:
        return redirect('/')

    isManager = True if (session['user']['role'] == "Project Manager") else False
    print("session softskills: ",session['softSkills'])
    return render_template('/softSkills.html', isManager=isManager, defaultValues = session['softSkills'])

# project manager homepage
@app.route('/managerHome')
def managerHome():
    if 'user' not in session:
        return redirect('/')

    # user = ProjectManager(session['user']['email'])
    userProjects = ProjectManager.createUserProjects(session['currentProjects'])

    currentProjects = []
    for project in userProjects:
        currentProjects.append(as_dict(project))

    pastUserProjects = ProjectManager.createUserProjects(session['pastProjects'])

    successProjects = []
    failureProjects = []
    cancelledProjects = [] 

    for project in pastUserProjects:
        projectDict = as_dict(project)
        projectDict['project_risk_state'] = (ProjectRisk.query.filter_by(project_id = projectDict['project_id']).first()).project_risk_state

        if project.project_state == "Success":
            successProjects.append(projectDict)
        elif project.project_state == "Failure":
            failureProjects.append(projectDict)
        else:
            cancelledProjects.append(projectDict)

    print(session['currentProjects'])
    print(currentProjects)

    return render_template('/managerHome.html',name=session['user']['first_name'],greenProjects=currentProjects,
                           successfulProjects = successProjects, failedProjects = failureProjects, cancelledProjects = cancelledProjects)

# create a project
@app.route('/createProject', methods = ['GET', 'POST'])
def proj():
    if 'user' not in session:
        return redirect('/')
    
    session['projectDevelopers'] = []
    session['projectRequirements'] = []

    allDevelopers = User.query.filter_by(role="Developer").all()
    return render_template('/createProject.html', allDevelopers=allDevelopers)

# see project info
@app.route('/projectInfo')
def projectInfo():
    if 'currentProject' not in session:
        return redirect('/managerHome')
    currentProject = session['currentProject']
    return render_template('/projectInfo.html',project = session['currentProject'], softSkillValues = [], projectReqLabels = [], projectReqValues = [], budgetComp = [], timeComp = [], commitsByDay = [], commitsByHour = [], developerData = [])

# update a project via project info
@app.route('/updateProject')
def updateProject():
    if ('budgetComponents' or 'timeComponents' or 'currentProject') not in session:
        return redirect('/managerHome')
    
    print("budgetComponents:", session['budgetComponents'])
    print("timeComponents:", session['timeComponents'])

    allDevelopers = User.query.filter_by(role="Developer").all()
    print(session["projectDevelopers"])
    currentDevelopers = User.query.filter(User.id.in_(session['projectDevelopers'])).all()
    return render_template('/updateProject.html', project = session['currentProject'], budgetComponents = session['budgetComponents'],
                            timeComponents = session['timeComponents'], currentDevelopers = currentDevelopers, currentSkills = session['projectRequirements'],
                            allDevelopers = allDevelopers)

# //RENDER_TEMPLATES =============================================================================================================

# REDIRECTS ======================================================================================================================
# login handler
@app.route('/loginRedirect', methods = ['POST'])
def loginRedirect():
    email = request.form['email']
    password = request.form['password']
    actor = UserClass.authenticateUser(email,password)

    if actor == "Developer":
        user = Developer(email)
        
        session['user'] = as_dict(user.user)
        session['softSkills'] = as_dict(user.softSkills)
        session['currentProjects'] = user.currentProjects
        session['pastProjects'] = user.pastProjects
        session['strengths'] = user.strengths

        return redirect('/developerHome')
    elif actor == "Project Manager":
        user = ProjectManager(email)
        
        session['user'] = as_dict(user.user)
        session['softSkills'] = as_dict(user.softSkills)
        session['currentProjects'] = user.currentProjects
        session['pastProjects'] = user.pastProjects
        for project in session['currentProjects']:
            print(project)
            calculateRisk(project)
        return redirect('/managerHome')
    else:
        flash("Wrong Email or Password")
        return redirect('/')

# register handler
@app.route('/registerRedirect', methods = ['POST'])
def newUser():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    # confpassword = request.form['confpassword']
    # HAVE FRONT END CHECK THEY ARE THE SAME AND THEN DONT SEND IN FORM

    if((User.query.filter_by(email=email).first()) is not None):
        flash("Username already taken")
        return redirect('/register')
    
    if request.form.get("myCheck"):
        manager = True
        ProjectManager.insertUser("Project Manager", firstname, lastname, email, password)

        user = ProjectManager(email)

        session['user'] = as_dict(user.user)
        session['softSkills'] = as_dict(user.softSkills)
        session['currentProjects'] = user.currentProjects
        session['pastProjects'] = user.pastProjects

        # print(session['user']['first_name'])

        # add colour risk estimates once cost function is done
        currentProjectGreen = []
        currentProjectAmber = []
        currentProjectRed = []
        # for project in session['currentProjects']:
        #     currentProjectGreen.append(ProjectsClass(project.project_id))

        return redirect('/managerHome')
    else:
        manager = False
        Developer.insertUser("Developer", firstname, lastname, email, password)

        user = Developer(email)
        
        session['user'] = as_dict(user.user)
        session['softSkills'] = as_dict(user.softSkills)
        session['currentProjects'] = user.currentProjects
        session['pastProjects'] = user.pastProjects
        session['strengths'] = user.strengths

        # print(session['user']['first_name'])
        # add colour risk estimates once cost function is done
        currentProjectGreen = []
        currentProjectAmber = []
        currentProjectRed = []
        # for project in session['currentProjects']:
        #     currentProjectGreen.append(ProjectsClass(project.project_id))

        return redirect('/developerHome')

# logout handler
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# update soft skills
@app.route('/updateSoftSkills', methods = ['POST'])
def updateSoftSkills():
    enthusiasm = request.form['enthusiasm']
    purpose = request.form['purpose']
    challenge = request.form['challenge']
    health = request.form['health']
    resilience = request.form['resilience']
    print(enthusiasm)
    print(purpose)
    print(challenge)
    print(health)
    print(resilience)
    # db.session.add(UserSkills(current_user.id, enthusiasm, purpose, challenge, health, resilience))
    # db.session.commit()
    UserClass.updateSoftSkills(session['user']['id'],[enthusiasm,purpose,challenge,health,resilience])

    user_id = session['softSkills']['user_id']
    user_skill_id = session['softSkills']['user_skill_id']

    session['softSkills'] = {"enthusiasm": enthusiasm, "purpose":purpose,"challenge":challenge,"health":health,"resilience":resilience,"user_id":user_id,"user_skill_id":user_skill_id}

    if session['user']['role'] == "Project Manager":
        return redirect('/managerHome')
    else:
        return redirect('/developerHome')

# manager create project button
@app.route('/createProjectRedirect', methods = ['POST'])
def createProjectRedirect():
    if request.method == 'POST':
        projectName = request.form['project_name']
        projectDescription = request.form['project_description']

        repo_owner = session['user']['id']
        repo_name = request.form['repo_name']

        deadline = request.form['deadline']
        budget = request.form['budget']

        # def insertProject(project_manager_id, project_name, deadline, budget, project_state, description, repo_name, developers, requirements):
        thisProjectID = ProjectsClass.insertProject(session['user']['id'], projectName, deadline, budget, "Ongoing", projectDescription,repo_name, session['projectDevelopers'], session['projectRequirements'])
        # thisProject = Projects.query.order_by(Projects.project_id.desc()).first()
        update = session['currentProjects']
        update.append(thisProjectID)
        session['currentProjects'] = update

    return redirect('/managerHome')

# manager see project info
@app.route('/projectInfoRedirect', methods = ['POST'])
def projectInfoRedirect():

    if request.method == 'POST':
        projectID = request.form['project_id']
        thisProject = Projects.query.filter_by(project_id = projectID).first()

        # needs a list of dictionaries
        thisProjectRiskID = (ProjectRisk.query.filter_by(project_id = projectID).first()).project_risk_id

        session['currentProject'] = {"project_id" : projectID, "project_name" : thisProject.project_name, "project_risk_id" : thisProjectRiskID}
    return redirect('/projectInfo')

# update project via project info
@app.route('/updateProjectRedirect', methods = ['POST'])
# needs a list of dictionaries
def updateProjectRedirect():
    if request.method == 'POST':
        thisProjectRiskID = session['currentProject']['project_risk_id']

        costComponentObjects = RiskComponent.query.filter_by(project_risk_id = thisProjectRiskID, risk_type = "Cost").all()
        budgetComponents = []

        for component in costComponentObjects:
            budgetComponents.append(as_dict(component))

        timeComponentObjects = RiskComponent.query.filter_by(project_risk_id = thisProjectRiskID, risk_type = "Time").all()
        timeComponents = []

        for component in timeComponentObjects:
            timeComponents.append(as_dict(component))

        session['budgetComponents'] = budgetComponents
        session['timeComponents'] = timeComponents

        projectRequirementObjects = ProjectRequirement.query.filter_by(project_id = session['currentProject']['project_id']).all()
        requirements = []
        for requirement in projectRequirementObjects:
            requirements.append(requirement.requirement)
        
        session['projectRequirements'] = requirements

        developerObjects = DeveloperProject.query.filter_by(project_id = session['currentProject']['project_id']).all()
        developers = []
        for developer in developerObjects:
            developers.append(str(User.query.filter_by(id = developer.developer_id).first().id))
        session['projectDevelopers'] = developers
    
    return redirect('/updateProject')
# //REDIRECTS ======================================================================================================================

# AJAX HANDLERS ====================================================================================================================
@app.route('/addDeveloperSkill', methods = ['POST'])
def addDeveloperSkill():
    
    skillName = request.form['skillName']
    # check if the skill already exists in the db
    check = DeveloperStrength.query.filter((DeveloperStrength.developer_id == session['user']['id']) & (DeveloperStrength.strength == skillName)).first()

    # new skill
    if check is None:
        db.session.add(DeveloperStrength(session['user']['id'], skillName))
        db.session.commit()
        update = session['strengths']
        update.append(skillName)
        session['strengths'] = update
        print("add developer skills: ",session['strengths'])
        return "OK"
    # else, the function is not "succesfull", and so the js does not add the skill either

@app.route('/removeDeveloperSkill', methods = ['POST'])
def removeDeveloperSkill():

    skillName = request.form['skillName']
    DeveloperStrength.query.filter((DeveloperStrength.developer_id == session['user']['id']) & (DeveloperStrength.strength == skillName)).delete()
    db.session.commit()
    update = session['strengths']
    update.remove(skillName)
    session['strengths'] = update
    print("remove developer skills: ",session['strengths'])
    return "OK"



# update project page =============================
# add developer to session (not commited to database)
@app.route('/addDevToProjectList', methods = ['POST'])
def addDevToProjectList():
    print("current developers:", session['projectDevelopers'])
    if request.form['devId'] not in session['projectDevelopers']:
        update = session['projectDevelopers']
        update.append(request.form['devId'])
        session['projectDevelopers'] = update
        print(session['projectDevelopers'])
        return "OK"

# remove developer from session (not commited to database)
@app.route('/removeDevFromProjectList', methods = ['POST'])
def removeDevFromProjectList():
    update = session['projectDevelopers']
    update.remove(request.form['devId'])
    session['projectDevelopers'] = update
    print(session['projectDevelopers'])
    return "OK"

# add requirement to session (not commited to database)
@app.route('/addReqToProjectList', methods = ['POST'])
def addReqToProjectList():
    if request.form['reqName'] not in session['projectRequirements']:
        update = session['projectRequirements']
        update.append(request.form['reqName'])
        session['projectRequirements'] = update
        print(session['projectRequirements'])
        return "OK"

# remove requirement from session (not commited to database)
@app.route('/removeReqFromProjectList', methods = ['POST'])
def removeReqFromProjectList():
    update = session['projectRequirements']
    update.remove(request.form['reqName'])
    session['projectRequirements'] = update
    session['projectRequirements']
    return "OK"

# add time or cost component to project
@app.route('/submitCostComponent', methods=['POST'])
def submitCostComponent():
    if request.method == 'POST':
        componentName = request.form['name']

        thisComponent = RiskComponent.query.filter_by(name = componentName, project_risk_id = session['currentProject']['project_risk_id']).first()

        if thisComponent:
            raise ValueError("Name already in database")

        else:
            db.session.add(RiskComponent(session['currentProject']['project_risk_id'], componentName, request.form['best'], request.form['worst'], request.form['average'], request.form['absval'], request.form['type']))
            db.session.commit()

            #print(request.form['type'])
            if request.form['type'] == "Time":
                update = session['timeComponents']
                update.append(as_dict(RiskComponent.query.filter_by(name = componentName).first()))
                session['timeComponents'] = update
            else:
                update = session['budgetComponents']
                update.append(as_dict(RiskComponent.query.filter_by(name = componentName).first()))
                session['budgetComponents'] = update
        
        return "OK"

# remove a time or cost component from project
@app.route('/removeCostComponent', methods=['POST'])
def removeCostComponent():
    if request.method == 'POST':
        componentName = request.form['name']
        RiskComponent.query.filter_by(name = componentName, project_risk_id = session['currentProject']['project_risk_id']).delete()
        db.session.commit()
        if request.form['type'] == "Time":
            update = session['timeComponents']
            update = list(filter(lambda x: x['name'] != componentName, update))
            session['timeComponents'] = update
        else:
            update = session['budgetComponents']
            update = list(filter(lambda x: x['name'] != componentName, update))
            session['budgetComponents'] = update

        return "OK"
    


# change and commit description change
@app.route('/changeDescription', methods = ['POST'])
def changeDescription():
    if request.method == 'POST':
        thisProject = Projects.query.filter_by(project_id = session['currentProject']['project_id']).first()
        thisProject.description = request.form['description']
        db.session.commit()
        return "OK"

# change and commit status change (this will move the project to pastProject)
@app.route('/changeStatus', methods = ['POST'])
def changeStatus():
    if request.method == 'POST':
        status = request.form['status']
        thisProject = Projects.query.filter_by(project_id = session['currentProject']['project_id']).first()
        thisProject.project_state = status
        db.session.commit()

        print(session['currentProjects'])
        print(session['currentProject']['project_id'])
  
        update = session['currentProjects']
        update.remove(thisProject.project_id)
        session['currentProjects'] = update

        update = session['pastProjects']
        update.append(thisProject.project_id)
        session['pastProjects'] = update
            
        return "OK"

# commit changes to developers
@app.route('/updateDevelopers', methods=['POST'])
def updateDevelopers():
    if request.method == 'POST':
        developerIDs = session['projectDevelopers']
        projectID = session['currentProject']['project_id']

        # with db.engine.connect() as conn:
        #     for developer in developerIDs:
        #         conn.execute(f"INSERT OR IGNORE INTO developer_project (developer_id, project_id) VALUES ('{developer}','{projectID})")
        #     db.session.commit()
        # stmt = DeveloperProject.insert(developer,projectID).prefix_with('IGNORE')
        DeveloperProject.query.filter_by(project_id = projectID).delete()
        for developer in developerIDs:
            # check = DeveloperProject.query.filter_by(developer_id = developer, project_id = projectID).first()
            # if not check:
            db.session.add(DeveloperProject(developer, projectID))

        db.session.commit()
            
        return "OK"

# commite changes to requirements
@app.route('/updateRequirements', methods = ['POST'])
def updateRequirements():
    if request.method == 'POST':
        requirements = session['projectRequirements']
        projectID = session['currentProject']['project_id']

        ProjectRequirement.query.filter_by(project_id = projectID).delete()
        for item in requirements:
            # check = ProjectRequirement.query.filter_by(project_id = projectID, requirement = item).first()
            # if not check:
            db.session.add(ProjectRequirement(projectID, item))
        
        db.session.commit()

        return "OK"
# //update project page =============================

# //AJAX HANDLERS ==================================================================================================================

# @app.route('/confirmDeveloperSkills', methods = ['POST'])
# def confirmDeveloperSkills():
#     if request.method == 'POST':
#         strengths = session['strengths']
#         developerID = session['user']['id']

#         DeveloperStrength.query.filter_by(developer_id = developerID).delete()

#         for item in strengths:
#             db.session.add(DeveloperStrength(developerID,item))
        
#         db.session.commit()

#         return "OK"
