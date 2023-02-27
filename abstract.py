from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask
from schema import db, User, UserSkills, TimeComponent, CostComponent

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

    def authenticateUser(email, password):
        # obtain password hash from the database using email
        with app.app_context():
            actor = User.query.filter_by(email = email).first()
        
        # if match return the type of user
        if actor and check_password_hash(actor.password_hash, password):
            return actor.role

        return False

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

    def __init__(self,componentID,type):
        if type == "Time":
            with app.app_context():
                self.component = TimeComponent.query.filter_by(time_component_id = componentID).first()
        elif type == "Cost":
            with app.app_context():
                self.component = CostComponent.query.filter_by(cost_component_id = componentID).first()
    


