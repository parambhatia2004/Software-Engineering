from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask

from abstract import UserClass, RiskComponentClass
from schema import db, Projects, ProjectRisk, DeveloperProject, ProjectRequirement

app = Flask(__name__)
app.secret_key = 'SecRetKeyHighLyConFiDENtIal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RiskTracker.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

class ProjectManager(UserClass):

    def updateProjects(projectID, action):
        pass


class Developer(UserClass):
    
    # need new init with strengths!!!
    def __init__(self, email):
        super(Developer,self).__init__(email)
        self.strengths = ["Python", "Java"]


    def updateProjects(projectID, action):
        pass
    
    # def updateProjects(projectID, action):
    #     return super().updateProjects(action)


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
            requirements = ProjectRequirement.query.filter_by(project_id = self.project.project_id).all()
            for item in requirements:
                self.requirements.append(item.requirement)

            self.riskEstimate = ProjectRisk.query.filter_by(project_id = self.project.project_id).first()

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


class TimeComponentClass(RiskComponentClass):
    def __init__(self, ID):
        super(TimeComponentClass, self).__init__(ID, "Time")

class CostComponentClass(RiskComponentClass):
    def __init__(self,ID):
        super(CostComponentClass,self).__init__(ID, "Cost")



# cost function work needed
class RiskEstimateClass():
    def __init__(self, projectRiskID):
        with app.app_context():
            self.risk = ProjectRisk.query.filter_by(project_risk_id = projectRiskID).first()


    def applySoftSkillWeighting(softSkills):
        pass

    def monteCarlo():
        pass






actor = ProjectManager.authenticateUser("Matt@gmail","asdf")
if actor == "Developer":
    print("Developer authentication successful")
    matt = Developer("Matt@gmail")
    # matt.changePassword("asdf","asdf123")
    print("Enthusiasm before change: ",matt.softSkills.enthusiasm)
    matt.updateSoftSkills([10,11,12,13,14])
    print("Enthusiasm after change: ",matt.softSkills.enthusiasm)
    print("Developer Strengths: ", matt.strengths)
elif actor == "Project Manager":
    print("Project Manager authentication successful")
    matt = Developer("test123")
    matt.changePassword("qwerty","qwerty123")
else:
    print("authentication unsuccessful")


testProject = ProjectsClass(1)
print("Original name: ", testProject.project.project_name)
testProject.setProjectName('Ham Sandwich')
print("Name after change: ", testProject.project.project_name)