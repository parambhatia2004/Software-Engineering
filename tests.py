from concrete import Developer, ProjectManager
from schema import *
import unittest
from schema import db, User, UserSkills, RiskComponent, DeveloperProject, Projects
from flask import Flask
from sqlalchemy import select

app = Flask(__name__)
app.secret_key = 'SecRetKeyHighLyConFiDENtIal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RiskTracker.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


class Testing(unittest.TestCase):

    # TO-DO insert multiple users using a for loop 
    # confirms insertUser() adds users to the User table 
    def test_0_insertUser(self):
        Developer.insertUser("Developer", "Brindan", "asdf", "brindan@gmail", "asdf")
        with app.app_context(): 
            actor = User.query.filter_by(email = "brindan@gmail").first()
        self.assertEqual(actor.email, "brindan@gmail")


    # confirms authenticateUser() authenticates users in the User table when passed the correct email and password 
    def test_1_authenticateUser(self):
        # from test_0 we know that Brindan has been added to the User table
        role = Developer.authenticateUser("brindan@gmail","asdf")
        self.assertEqual(role, "Developer")


    # confirms changePassword() changes the password hash in the User table 
    def test_2_changePassword(self):
        print("Start changePassword test\n")
        brindan = Developer("brindan@gmail")

        old_password_hash = brindan.user.password_hash
        print("pre change password: ", old_password_hash)

        brindan.changePassword("asdf","newpassword")

        new_password_hash = brindan.user.password_hash
        print("post change password: ", new_password_hash)

        self.assertNotEqual(old_password_hash, new_password_hash)
        print("\nFinish changePassword test\n")


    # confirms updateSoftSkills() updates soft skill values in the UserSkills table 
    def test_3_updateSoftSkills(self):
        print("Start updateSoftSkills test\n")
        brindan = Developer("brindan@gmail")
        with app.app_context():
            soft_skills = UserSkills.query.filter_by(user_id = brindan.user.id).first()

        print("pre update soft skills: ", soft_skills.enthusiasm, soft_skills.purpose, soft_skills.challenge, soft_skills.health, soft_skills.resilience)

        brindan.updateSoftSkills([1,2,3,4,5])
        with app.app_context():
            soft_skills = UserSkills.query.filter_by(user_id = brindan.user.id).first()

        soft_skills_list = []
        soft_skills_list.append(soft_skills.enthusiasm)
        soft_skills_list.append(soft_skills.purpose)
        soft_skills_list.append(soft_skills.challenge)
        soft_skills_list.append(soft_skills.health)
        soft_skills_list.append(soft_skills.resilience)
        self.assertEqual(soft_skills_list, [1,2,3,4,5])

        print("post update soft skills: ", soft_skills_list)
        print("\nFinish updateSoftSkills test\n")
    

if __name__ == '__main__':
    unittest.main()
    





# Developer.insertUser("Developer", "Brindan", "asdf", "brindan@gmail", "asdf")
# brindan = Developer("brindan@gmail")

# actor = ProjectManager.authenticateUser("brindan@gmail","asdf")
# print(actor)

# print("pre change password: ", brindan.user.password_hash)
# brindan.changePassword("asdf","newpassword")
# print("post change: ", brindan.user.password_hash)




