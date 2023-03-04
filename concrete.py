from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask

from abstract import UserClass, RiskComponentClass
from schema import db, Projects, ProjectRisk, DeveloperProject, ProjectRequirement, DeveloperStrength, RiskComponent, ProjectGitHub
from sqlalchemy import or_

import datetime

app = Flask(__name__)
app.secret_key = 'SecRetKeyHighLyConFiDENtIal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RiskTracker.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Project manager concrete class, uses the user abstract class for most of its functions
class ProjectManager(UserClass):

    def __init__(self, email):
        super(ProjectManager,self).__init__(email)

        with app.app_context():
            # obtain current project IDs
            currentProjects = Projects.query.filter_by(project_manager_id = self.user.id, project_state = "Ongoing").all()
            self.currentProjects = []
            for project in currentProjects:
                self.currentProjects.append(project.project_id)

            # obtain past project IDs
            pastProjects = Projects.query.filter(Projects.project_manager_id == self.user.id, or_(Projects.project_state == "Success",Projects.project_state == "Failure",
            Projects.project_state == "Cancelled")).all()
            self.pastProjects = []
            for project in pastProjects:
                self.pastProjects.append(project.project_id)

    # !!!
    def updateProjects(projectID, action):
        pass



# Developer concrete class
class Developer(UserClass):
    
    def __init__(self, email):
        super(Developer,self).__init__(email)
        
        with app.app_context():
            # obtain current project IDs
            currentProjects = DeveloperProject.query.join(Projects).filter(DeveloperProject.developer_id==self.user.id, 
            Projects.project_state == "Ongoing").with_entities(DeveloperProject.project_id).all()
            self.currentProjects = []
            for project in currentProjects:
                self.currentProjects.append(project[0])

            # obtain past project IDs
            pastProjects = DeveloperProject.query.join(Projects).filter(DeveloperProject.developer_id==self.user.id,
            or_(Projects.project_state == "Success",Projects.project_state == "Failure",
            Projects.project_state == "Cancelled")).with_entities(DeveloperProject.project_id).all()
            self.pastProjects = []
            for project in pastProjects:
                self.pastProjects.append(project[0])


            self.strengths = []
            strengths = DeveloperStrength.query.filter_by(developer_id = self.user.id).all()
            for item in strengths:
                self.strengths.append(item.strength)

    # !!!
    def updateProjects(projectID, action):
        pass
    

# Project concrete class
class ProjectsClass():

    def __init__(self,projectID):
        with app.app_context():
            self.project = Projects.query.filter_by(project_id = projectID).first()

            # all the developers on this project
            team = DeveloperProject.query.filter_by(project_id = self.project.project_id).all()

            self.team = []
            for member in team:
                self.team.append(member.developer_id)
            
            self.requirements = []
            # all requirements linked to this projectID
            requirements = ProjectRequirement.query.filter_by(project_id = self.project.project_id).all()
            for item in requirements:
                self.requirements.append(item.requirement)

            # Project risk linked to this projectID
            self.riskEstimate = RiskEstimateClass(self.project.project_id)

            self.gitHub = ProjectGitHub.query.filter_by(project_id = self.project.project_id).first()

    # insert project AND create a project risk row for it in the database
    @staticmethod
    def insertProject(project_manager_id, project_name, deadline, budget, project_state, description):
        with app.app_context():
            db.session.add(Projects(project_manager_id,project_name,deadline,budget,project_state,description))
            db.session.commit()

            thisProject = Projects.query.order_by(Projects.project_id.desc()).first()
            db.session.add(ProjectRisk(thisProject.project_id,None,None,None))
            db.session.add(ProjectGitHub(thisProject.project_id,None,None,None,None))
            db.session.commit()


    # Setters - changes both the object that calls it and the SQL database info
    def setProjectName(self, newName):
        with app.app_context():
            updatedProject = Projects.query.filter_by(project_id = self.project.project_id).first()
            updatedProject.project_name = newName
            db.session.commit()

            self.project.project_name = newName
    
    def setProjectDeadline(self, newDeadline):
        with app.app_context():
            updatedProject = Projects.query.filter_by(project_id = self.project.project_id).first()
            updatedProject.deadline = newDeadline
            db.session.commit()

            self.project.deadline = newDeadline
    
    def setProjectBudget(self, newBudget):
        with app.app_context():
            updatedProject = Projects.query.filter_by(project_id = self.project.project_id).first()
            updatedProject.budget = newBudget
            db.session.commit()

            self.project.budget = newBudget

    def setProjectState(self, newState):
        states = ["Success", "Failure", "Ongoing", "Cancelled"]

        if newState in states:
            with app.app_context():
                updatedProject = Projects.query.filter_by(project_id = self.project.project_id).first()
                updatedProject.project_state = newState
                db.session.commit()

                self.project.project_state = newState
    
    def setProjectDescription(self, newDescription):
        with app.app_context():
            updatedProject = Projects.query.filter_by(project_id = self.project.project_id).first()
            updatedProject.description = newDescription
            db.session.commit()

            self.project.description = newDescription
    
    def updateGitHub(self, repoData):
        if len(repoData) == 4:
            with app.app_context():
                changeRepo = ProjectGitHub.query.filter_by(project_id = self.project.project_id).first()
                changeRepo.repo_name = repoData[0]
                changeRepo.issues_24 = repoData[1]
                changeRepo.issues_7 = repoData[2]
                changeRepo.time_of_day = repoData[3]

                db.session.commit()

                self.gitHub.repo_name = repoData[0]
                self.gitHub.issues_24 = repoData[1]
                self.gitHub.issues_7 = repoData[2]
                self.gitHub.time_of_day = repoData[3]

            return True

        return False
    

# currently unused
# Time component class
class TimeComponentClass(RiskComponentClass):
    def __init__(self, ID):
        super(TimeComponentClass, self).__init__(ID)

# currently unused
# Cost component class
class CostComponentClass(RiskComponentClass):
    def __init__(self,ID):
        super(CostComponentClass,self).__init__(ID)


# COST FUNCTION HERE NEEDS WORK
class RiskEstimateClass():
    def __init__(self, projectID):
        with app.app_context():
            self.risk = ProjectRisk.query.filter_by(project_id = projectID).first()
            self.timeComponents = RiskComponent.query.filter_by(project_risk_id = self.risk.project_risk_id, risk_type = "Time").all()
            self.riskComponents = RiskComponent.query.filter_by(project_risk_id = self.risk.project_risk_id, risk_type = "Cost").all()

    # !!!
    def applySoftSkillWeighting(softSkills):
        pass

    # !!!
    def monteCarlo():
        pass





# TESTING
# actor = ProjectManager.authenticateUser("Matt@gmail","asdf")
# if actor == "Developer":
#     print("Developer authentication successful")
#     matt = Developer("Matt@gmail")
#     # matt.changePassword("asdf","asdf123")
#     print("Enthusiasm before change: ",matt.softSkills.enthusiasm)
#     matt.updateSoftSkills([10,11,12,13,14])
#     print("Enthusiasm after change: ",matt.softSkills.enthusiasm)
#     print("Developer Strengths: ", matt.strengths)
#     print("Developer current projects: ", matt.currentProjects)
#     print("Developer past projects: ", matt.pastProjects)
# elif actor == "Project Manager":
#     print("Project Manager authentication successful")
#     matt = Developer("test123")
#     matt.changePassword("qwerty","qwerty123")
# else:
#     print("authentication unsuccessful")



# testProject = ProjectsClass(1)
# print("Original name: ", testProject.project.project_name)
# testProject.setProjectName('Ham Sandwich')
# print("Name after change: ", testProject.project.project_name)

# Developer.insertUser("Developer","Insert","Method","@123","test")
# ProjectsClass.insertProject(2,"insertProject",23,45,"Ongoing","This was inserted with method")

# project4 = ProjectsClass(4)
# project4.updateGitHub(["Changed",32,54,datetime.time(10,29)])

# oscar = ProjectManager("Oscar@gmail")
# print("Oscars current projecs:", oscar.currentProjects)
# print("Oscars past projects:", oscar.pastProjects)

# oscarsProjects = oscar.createUserProjects()
# print("Oscars projects: ", oscarsProjects)

# mattsProjects = matt.createUserProjects()
# print("Matts projects:", mattsProjects)

# print("Matts Projects by name:")
# for project in mattsProjects:
#     print("Project Name:", project.project_name)