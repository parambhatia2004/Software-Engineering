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

from schema import db, User, dbinit
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
    if security.check_password_hash(user.password, password):
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