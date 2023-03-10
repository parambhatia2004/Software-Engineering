from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint

from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class Projects(db.Model):
    __tablename__ = 'projects'

    # Primary and Foreign keys
    project_id = db.Column(db.Integer, primary_key=True)
    project_manager_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    # Fields
    project_name = db.Column(db.String(255), nullable=False)
    deadline = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    project_state = db.Column(db.String(20), CheckConstraint("project_state IN ('Success', 'Failure', 'Ongoing', 'Cancelled')"), nullable=False)
    description = db.Column(db.String(255))

    def __init__(self, project_manager_id, project_name, deadline, budget, project_state, description):
        self.project_manager_id = project_manager_id
        self.project_name = project_name
        self.deadline = deadline
        self.budget = budget
        self.project_state = project_state
        self.description = description

class ProjectRequirement(db.Model):
    __tablename__ = 'project_requirement'

    # Primary and Foreign keys
    requirement_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)

    # Fields
    requirement = db.Column(db.String(255), nullable=False)

    def __init__(self, project_id, requirement):
        self.project_id = project_id
        self.requirement = requirement

class ProjectRisk(db.Model):
    __tablename__ = 'project_risk'

    # Primary and Foreign keys
    project_risk_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), unique=True, nullable=False)

    # Fields
    monte_carlo_time = db.Column(db.Integer)
    monte_carlo_cost = db.Column(db.Integer)
    project_risk_state = db.Column(db.String(20), CheckConstraint("project_risk_state IN ('Green', 'Amber', 'Red')"))
    # project_risk_value = db.Column(db.Float)

    def __init__(self, project_id, monte_carlo_time, monte_carlo_cost, project_risk_state):
        self.project_id = project_id
        self.monte_carlo_time = monte_carlo_time
        self.monte_carlo_cost = monte_carlo_cost
        self.project_risk_state = project_risk_state

# class TimeComponent(db.Model):
#     __tablename__ = 'time_component'

#     # Primary and Foreign keys
#     time_component_id = db.Column(db.Integer, primary_key=True)
#     project_risk_id = db.Column(db.Integer, db.ForeignKey('project_risk.project_risk_id', ondelete='CASCADE'), nullable=False)

#     # Fields
#     best = db.Column(db.Integer, nullable=False)
#     worst = db.Column(db.Integer, nullable=False)
#     average = db.Column(db.Integer, nullable=False)
#     absolute_value = db.Column(db.Integer, nullable=False)

#     def __init__(self, project_risk_id, best, worst, average, absolute_value):
#         self.project_risk_id = project_risk_id
#         self.best = best
#         self.worst = worst
#         self.average = average
#         self.absolute_value = absolute_value

# class CostComponent(db.Model):
#     __tablename__ = 'cost_component'

#     # Primary and Foreign keys
#     cost_component_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     project_risk_id = db.Column(db.Integer, db.ForeignKey('project_risk.project_risk_id', ondelete='CASCADE'), nullable=False)

#     # Fields
#     best = db.Column(db.Integer, nullable=False)
#     worst = db.Column(db.Integer, nullable=False)
#     average = db.Column(db.Integer, nullable=False)
#     absolute_value = db.Column(db.Integer, nullable=False)

    # def __init__(self, project_risk_id, best, worst, average, absolute_value):
    #     self.project_risk_id = project_risk_id
    #     self.best = best
    #     self.worst = worst
    #     self.average = average
    #     self.absolute_value = absolute_value

class ProjectGitHub(db.Model):
    __tablename__ = 'project_git_hub'

    # Primary and Foreign keys
    repo_id = db.Column(db.Integer, primary_key=True)
    project_id =  db.Column(db.Integer, db.ForeignKey('projects.project_id', ondelete='CASCADE'), unique=True, nullable=False)

    # Fields
    # repo_owner_name = db.Column(db.String(255))
    repo_name = db.Column(db.String(255))
    issues_24 = db.Column(db.Integer)
    issues_7 = db.Column(db.Integer)
    time_of_day = db.Column(db.Time)

    def __init__(self, project_id,repo_name,issues_24,issues_7,time_of_day):
        self.project_id = project_id
        self.repo_name = repo_name
        self.issues_24 = issues_24
        self.issues_7 = issues_7
        self.time_of_day = time_of_day

        # 2? time stamps


class RiskComponent(db.Model):
    __tablename__ = 'risk_component'

    # Primary and Foreign keys
    risk_component_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_risk_id = db.Column(db.Integer, db.ForeignKey('project_risk.project_risk_id', ondelete='CASCADE'), nullable=False)

    # Fields
    name = db.Column(db.String(255), nullable=False, unique=True)
    best = db.Column(db.Integer, nullable=True)
    worst = db.Column(db.Integer, nullable=True)
    average = db.Column(db.Integer, nullable=True)
    absolute_value = db.Column(db.Integer, nullable=True)
    risk_type = db.Column(db.String(20),CheckConstraint("risk_type IN ('Time', 'Cost')"))
    # risk_name = unique

    def __init__(self, project_risk_id, name, best, worst, average, absolute_value, risk_type):
        self.project_risk_id = project_risk_id
        self.name = name
        self.best = best
        self.worst = worst
        self.average = average
        self.absolute_value = absolute_value
        self.risk_type = risk_type


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Fields
    role = db.Column(db.String(20), CheckConstraint("role IN ('Developer', 'Project Manager')"), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def __init__(self, role, first_name, last_name, email, password_hash):
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash

class UserSkills(db.Model):
    __tablename__ = 'user_skills'

    # Primary and Foreign keys
    user_skill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Fields
    enthusiasm = db.Column(db.Integer)
    purpose = db.Column(db.Integer)
    challenge = db.Column(db.Integer)
    health = db.Column(db.Integer)
    resilience = db.Column(db.Integer)

    def __init__(self, user_id, enthusiasm, purpose, challenge, health, resilience):
        self.user_id = user_id
        self.enthusiasm = enthusiasm
        self.purpose = purpose
        self.challenge = challenge
        self.health = health
        self.resilience = resilience
# class Developers(db.Model):
#     __tablename__ = 'developers'

#     # Primary key
#     developer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

#     # Fields
#     first_name = db.Column(db.String(255), nullable=False)
#     last_name = db.Column(db.String(255), nullable=False)
#     email = db.Column(db.String(255), nullable=False, unique=True)
#     password_hash = db.Column(db.String(255), nullable=False)
#     enthusiasm = db.Column(db.Integer, nullable=False)
#     purpose = db.Column(db.Integer, nullable=False)
#     challenge = db.Column(db.Integer, nullable=False)
#     health = db.Column(db.Integer, nullable=False)
#     resilience = db.Column(db.Integer, nullable=False)

#     def __init__(self, first_name, last_name, email, password_hash, enthusiasm, purpose, challenge, health, resilience):
#         self.first_name = first_name
#         self.last_name = last_name
#         self.email = email
#         self.password_hash = password_hash
#         self.enthusiasm = enthusiasm
#         self.purpose = purpose
#         self.challenge = challenge
#         self.health = health
#         self.resilience = resilience

class DeveloperProject(db.Model):
    __tablename__ = 'developer_project'
    developer_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), primary_key=True)

    def __init__(self, developer_id, project_id):
        self.developer_id = developer_id
        self.project_id = project_id

class DeveloperStrength(db.Model):
    __tablename__ = 'developer_strength'
    strength_id = db.Column(db.Integer, primary_key=True)
    developer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    strength = db.Column(db.String(255))

    def __init__(self, developer_id, strength):
        self.developer_id = developer_id
        self.strength = strength

def dbinit():
    db.session.add(User('Developer','Matt', 'Jk', 'Matt@gmail', generate_password_hash("asdfasdf")))
    db.session.add(User('Project Manager', 'Oscar', 'Jk', 'Oscar@gmail', generate_password_hash("asdfasdf")))
    db.session.add(User('Developer','Ella', 'Jk', 'Ella@gmail', generate_password_hash("asdfasdf")))

    db.session.add(UserSkills('1','1','2','3','4','5'))
    db.session.add(UserSkills('2','1','2','3','4','5'))
    db.session.add(UserSkills('3','1','2','3','4','5'))

    db.session.add(Projects(2,'Test Project', 100, 200, 'Ongoing', 'This is a test project'))
    db.session.add(Projects(2,"Failed project",1,30,'Failure','This project failed'))
    db.session.add(Projects(2,"Another Project",300,7000,'Ongoing','This is a project'))
    db.session.add(Projects(2,"Failure 2",1,30,'Failure','This project also failed'))
    db.session.add(Projects(2,"Successful project",1,30,'Success','This project succeeded!'))
    db.session.add(Projects(2,"Cancelled project",1,30,'Cancelled','This project was cancelled'))


    db.session.add(DeveloperProject(1,1))
    db.session.add(DeveloperProject(1,2))
    db.session.add(DeveloperProject(1,3))

    db.session.add(ProjectRisk(1,None,None,None))
    db.session.add(ProjectRisk(2,None,None,"Red"))
    db.session.add(ProjectRisk(3,None,None,None))
    db.session.add(ProjectRisk(4,None,None,"Amber"))
    db.session.add(ProjectRisk(5,None,None,"Green"))
    db.session.add(ProjectRisk(6,None,None,"Amber"))

    db.session.add(RiskComponent(1,"Front End", 10,90,50,None,"Time"))
    db.session.add(RiskComponent(1,"Back End", 600,7000,550,None,"Time"))
    db.session.add(RiskComponent(1,"New Computer", 30,100,40,None,"Cost"))


    db.session.commit()





# from flask_sqlalchemy import SQLAlchemy
# from flask import Flask, render_template, jsonify, request, redirect, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# app = Flask(__name__)
# app.secret_key = 'test'

# # select the database filename
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.sqlite'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # set up a 'model' for the data you want to store
# # !!!!!

# from sqlalchemy import text

# # init the database so it can connect with our app
# db.init_app(app)

# # change this to False to avoid resetting the database every time this app is restarted
# # !!!!!!
# resetdb = True
# if resetdb:
#     with app.app_context():
#         # drop everything, create all the tables, then put some data into the tables
#         db.drop_all()
#         db.create_all()
#         dbinit()