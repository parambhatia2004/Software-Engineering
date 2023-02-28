from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask
from schema import db, User, UserSkills, RiskComponent, DeveloperProject, Projects
from sqlalchemy import or_

app = Flask(__name__)
app.secret_key = 'SecRetKeyHighLyConFiDENtIal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RiskTracker.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# abstract user class
class UserClass(ABC):

    def __init__(self, email):
        with app.app_context():
            self.user = User.query.filter_by(email=email).first()
            self.softSkills = UserSkills.query.filter_by(user_id = self.user.id).first()

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

    # Static
    @staticmethod
    def authenticateUser(email, password):
        # obtain password hash from the database using email
        with app.app_context():
            actor = User.query.filter_by(email = email).first()
        
        # if match return the type of user
        if actor and check_password_hash(actor.password_hash, password):
            return actor.role

        return False

    # will hash password, password parameter should be plain text
    @staticmethod
    def insertUser(role,first_name,last_name,email,password):
        password_hash = generate_password_hash(password)
        with app.app_context():
            db.session.add(User(role,first_name,last_name,email,password_hash))
            db.session.commit()

            thisUser = User.query.order_by(User.id.desc()).first()
            db.session.add(UserSkills(thisUser.id,None,None,None,None,None))
            db.session.commit()

    # Non Static
    # confirms old password and then updates the database with new password hash
    def changePassword(self, oldPassword, newPassword):
        if check_password_hash(self.user.password_hash, oldPassword):
            with app.app_context():
                newHash = generate_password_hash(newPassword)
                self.user.password_hash = newHash

                changepwd = User.query.filter_by(email = self.user.email).first()
                changepwd.password_hash = newHash
                db.session.commit()

            return True
        return False

    # takes in a 5 length int array and updates the soft skills to these values
    def updateSoftSkills(self, softSkills):

        if len(softSkills) == 5:
            with app.app_context():
                changeSoftSkills = UserSkills.query.filter_by(user_id = self.user.id).first()
                
                changeSoftSkills.enthusiasm = softSkills[0]
                changeSoftSkills.purpose = softSkills[1]
                changeSoftSkills.challenge = softSkills[2]
                changeSoftSkills.health = softSkills[3]
                changeSoftSkills.resilience = softSkills[4]
            
                db.session.commit()

                # self.softSkills = UserSkills.query.filter_by(user_id = self.user.id).first()
                self.softSkills.enthusiasm = softSkills[0]
                self.softSkills.purpose = softSkills[1]
                self.softSkills.challenge = softSkills[2]
                self.softSkills.health = softSkills[3]
                self.softSkills.resilience = softSkills[4]
        
            return True

        return False
    
    # decorator
    @abstractmethod
    def updateProjects(projectID, action):
        pass



# Abstract class for risk components (time and cost)
class RiskComponentClass(ABC):

    def __init__(self,componentID):
        with app.app_context():
            self.component = RiskComponent.query.filter_by(risk_component_id = componentID).first()
    
    @staticmethod
    def insertComponent(project_risk_id, best, worst, average, absolute_value, risk_type):
        with app.app_context():
            db.session.add(RiskComponent(project_risk_id,best,worst,average,absolute_value,risk_type))
            db.session.commit()


