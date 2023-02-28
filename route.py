from werkzeug import security
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)
app.secret_key = 'SecRetKeyHighLyConFiDENtIal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RiskTracker.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from schema import db, User, DeveloperStrength, UserSkills, dbinit
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
    results=DeveloperStrength.query.with_entities(DeveloperStrength.strength).filter_by(developer_id=current_user.id).all()
    results = [r[0] for r in results]
    return render_template('/developerSkills.html', currentSkills=results)

@app.route('/addDeveloperSkill', methods = ['POST'])
def addDeveloperSkill():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/login')
    skillName = request.form['skillName']
    # check if the skill already exists in the db
    temp = DeveloperStrength.query.filter((DeveloperStrength.developer_id == current_user.id) & (DeveloperStrength.strength == skillName)).first()
    # new skill
    if temp is None:
        db.session.add(DeveloperStrength(current_user.id, skillName))
        db.session.commit()
        results=DeveloperStrength.query.with_entities(DeveloperStrength.strength).filter_by(developer_id=current_user.id).all()
        results = [r[0] for r in results]
        return render_template('/developerSkills.html', currentSkills=results)
    # else, the function is not "succesfull", and so the js does not add the skill either

@app.route('/removeDeveloperSkill', methods = ['POST'])
def removeDeveloperSkill():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/login')
    skillName = request.form['skillName']
    temp = DeveloperStrength.query.filter((DeveloperStrength.developer_id == current_user.id) & (DeveloperStrength.strength == skillName)).delete()
    db.session.commit()
    results=DeveloperStrength.query.with_entities(DeveloperStrength.strength).filter_by(developer_id=current_user.id).all()
    results = [r[0] for r in results]
    return render_template('/developerSkills.html', currentSkills=results)

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
    db.session.add(UserSkills(current_user.id, enthusiasm, purpose, challenge, health, resilience))
    db.session.commit()
    if current_user.role == "manager":
        return render_template('/managerHome.html', name=current_user.first_name)
    else:
        return render_template('/developerHome.html', name=current_user.first_name)

@app.route('/softSkills')
def softSkills():
    isManager = False
    if current_user.role == "manager":
        isManager = True
    return render_template('/softSkills.html', isManager=isManager)

@app.route('/createProject')
def proj():
    allDevelopers = User.query.filter_by(role="developer").all()
    return render_template('/createProject.html', allDevelopers=allDevelopers)

@app.route('/managerHome')
def managerHome():
    return render_template('/managerHome.html', name=current_user.first_name)

@app.route('/developerHome')
def developerHome():
    return render_template('/developerHome.html', name=current_user.first_name)

@app.route('/createProjectRedirect')
def newProj():
    return render_template('/managerHome.html')

@app.route('/loginRedirect', methods = ['POST'])
def checkLogin():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()
    email=escape(email)
    if not user:
        return render_template('/login.html')

    if current_user.is_authenticated:
        if current_user.role == "manager":
            return render_template('/managerHome.html', name=current_user.first_name)
        else:
            return render_template('/developerHome.html', name=current_user.first_name)
    if security.check_password_hash(user.password_hash, password):
        login_user(user)

        if user.role == "manager":
            return render_template('/managerHome.html', name=user.first_name)
        else:
            return render_template('/developerHome.html', name=user.first_name)
    else:
        return render_template('/login.html')

@app.route('/registerRedirect', methods = ['POST'])
def newUser():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    confpassword = request.form['confpassword']
    if request.form.get("myCheck"):
        manager = True
    else:
        manager = False
    print(manager)
    if manager:
        role = "manager"
    else:
        role = "developer"
    if not email:
        flash("Enter email.")
        return redirect('/register')
    if not password:
        flash("Enter password.")
        return redirect('/register')
    if not confpassword:
        flash("Confirm password.")
        return redirect('/register')
    if not password == confpassword:
        flash("Passwords do not match.")
        return redirect('/register')

    if((User.query.filter_by(email=email).first()) is not None):
        flash("Username already taken")
        return redirect('/register')
    hashed_password = security.generate_password_hash(password)

    if security.check_password_hash(hashed_password, confpassword):
        db.session.add(User(role, firstname, lastname, email, hashed_password))
        db.session.commit()
        user = User.query.filter_by(email=email).first()
        login_user(user)
        if manager:
            return render_template('/managerHome.html', name=firstname)
        else:
            return render_template('/developerHome.html')

    else:
        flash("Passwords do not match.")
        return redirect('/register')

@app.route('/logout')
def logout():
    logout_user()
    return render_template('/login.html')