from concrete import Developer, ProjectManager
from schema import *

# check insertUser 
Developer.insertUser("Developer", "Brindan", "asdf", "brindan@gmail", "asdf")
brindan = Developer("brindan@gmail")

actor = ProjectManager.authenticateUser("asdf@gmail","asdf")
print(actor)

# check changePassword works when enterring the correct current password
# passwordChanged = Developer.changePassword(brindan, "asdf", "newpassword")
print("pre change password: ", brindan.user.password_hash)
brindan.changePassword("asdf","newpassword")
print("post change: ", brindan.user.password_hash)

# # how do we actually determine whether the password has been updated in db?

# # check changePassword does not work when entering the wrong current password 
# passwordChanged = Developer.changePassword(brindan, "newpassword1", "newpassword2")

# # check user skills have been initialised 
# print(UserSkills.query.filter_by(user_id = brindan.user.id).first()) #how do we see the database? 

# # check updateSoftSkills 
# Developer.updateSoftSkills(brindan, [1,2,3,4,5])
# print(UserSkills.query.filter_by(user_id = brindan.user.id).first())


