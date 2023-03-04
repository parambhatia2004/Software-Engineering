from trackGit import get_open_issues_count
from werkzeug import security
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import json
from concrete import *

app = Flask(__name__)
app.secret_key = 'SecRetKeyHighLyConFiDENtIal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RiskTracker.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from schema import db, User, DeveloperStrength, UserSkills, dbinit
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# change this to False to avoid resetting the database every time this app is restarted
resetdb = True
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()

def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def softSkillRisk(proj_id):
    return 0
def teamMemberRisk(proj_id):
    return 0

def monte_carlo(avg, best, worst):
    return 0

def calculateRisk(proj_id, avgTime, bestTime, worstTime, avgCost, bestCost, worstCost):
    proj_manager_id = current_user.id
    pm = User.query.filter_by(id=proj_manager_id).first().email
    #Thread open
    costMC = monte_carlo(avgTime, bestTime, worstTime)
    timeMC = monte_carlo(avgCost, bestCost, worstCost)
    #Thread close
    memberRisk = teamMemberRisk(proj_id)
    currentIssuesOpen = get_open_issues_count('calculator', 'microsoft')
    return currentIssuesOpen


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('/login.html')

@app.route('/register')
def reg():
    return render_template('/register.html')


@app.route('/developerSkills')
def developerSkills():
    # results=DeveloperStrength.query.with_entities(DeveloperStrength.strength).filter_by(developer_id=current_user.id).all()
    # results = [r[0] for r in results]
    return render_template('/developerSkills.html', currentSkills=session['strengths'])

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
        # return render_template('/developerSkills.html', currentSkills=session['strengths'])
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
    # return render_template('/developerSkills.html', currentSkills=session['strengths'])
    return "OK"

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

@app.route('/softSkills', methods = ['GET', 'POST'])
def softSkills():
    if 'user' not in session:
        return redirect('/')

    isManager = True if (session['user']['role'] == "Project Manager") else False
    print("session softskills: ",session['softSkills'])
    return render_template('/softSkills.html', isManager=isManager, defaultValues = session['softSkills'])

@app.route('/createProject', methods = ['GET', 'POST'])
def proj():
    if 'user' not in session:
        return redirect('/')
    
    allDevelopers = User.query.filter_by(role="Developer").all()
    return render_template('/createProject.html', allDevelopers=allDevelopers)

@app.route('/createProjectRedirect')
def newProj():
    return render_template('/managerHome.html')

@app.route('/loginRedirect', methods = ['POST'])
def checkLogin():
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

        return redirect('/managerHome')
    else:
        flash("Wrong Email or Password")
        return redirect('/')

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
    
@app.route('/managerHome')
def managerHome():
    if 'user' not in session:
        return redirect('/')

    # user = ProjectManager(session['user']['email'])
    userProjects = ProjectManager.createUserProjects(session['currentProjects'])

    currentProjects = []
    for project in userProjects:
        currentProjects.append(as_dict(project))

    print(session['currentProjects'])
    print(currentProjects)

    return render_template('/managerHome.html',name=session['user']['first_name'],greenProjects=currentProjects)

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

