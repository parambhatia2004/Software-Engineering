Data required and transmitted for frontend implementation
=========================================

Will add stuff here as I do the files

### login.html (DONE)
- flask route: `/login`, `/`
- redirects to `/loginRedirect`

### register.html (DONE)
- flask route: `/register`
- redirects to `/registerRedirect`

### managerHome.html
- flask route: `/managerHome`
- data required:
    - `name`
    - 3 lists of projects - one for green projects `greenProjects`, one for amber `amberProjects` and one for red `redProjects`;
    - the green list should contain for each project the name, id and description;
    - the amber and red lists should include everything the green one does, plus - for each project - a list of top risks (`project.toprisks`).
- data transmitted:
    - each project has a form (appears as just a button) attached that tracks the project id in a hidden variable; the form redirect to the `/projectInfoRedirect` route, and then the projectInfo page, getting the information for the correct project.

### createProject.html
- flask route: `/createProject`
- because we can't add a list of requirements or developers at once, whenever one is added in the form, use AJAX to add them to a (python) global list of developers/ requirements that should be attached to the project, and add the database associations when the submit button of the form is clicked
- transmits all project-specific variables
- form redirects to `/createProjectRedirect`
- ajax routes redirect to :
    - `/addDevToProjectList`
    - `/removeDevFromProjectList`
    - `/addReqToProjectList`
    - `/removeReqFromProjectList`
- data required: 
    - a list of all the registered developers, named `allDevelopers`


### projectInfo.html
- flask route: `/projectInfo`
- all data about a project
- let me know what we want to graph

### updateProject.html
- flask route: `/updateProject`
- redirects to `/updateProjectRedirect` (after that just go to the main page?)
- data required:
    - a project object with `project_id`, `project_name` 
    - a `timecomponent` and a `costcomponent` object,each with the `best`, `worst` and `average` attributes

### developerHome.html
- flask route: `/developerHome`
- data required: 
    - a list - `projects` that has for each project the project_name, description and deadline (I took the variable names from the db).

### developerSkills.html
- flask route: `developerSkills`
- data should be directly added to the database through ajax + flask
- redirection routes: `/addDeveloperSkill`, `/removeDeveloperSkill`
- data required: 
    - list of skills currently in the database for the developer, named `currentSkills`.

### softSkills.html (DONE)
- flask route: `/softSkills`
- data required:
    - an `isManager` global (session) variable in flask (used for redirecting to  the correct home menu from the soft skills page)
    - a `defaultvalues` array with the 5 soft skill variables that are currently in the database

### logout.html (DONE)
- flask route: /logout