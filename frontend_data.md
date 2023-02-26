Data required and transmitted for frontend implementation
=========================================

Will add stuff here as I do the files

### login.html
- flask route: `/login`, `/`
- redirects to `/loginRedirect`

### register.html
- flask route: `/register`
- redirects to `/registerRedirect`

### managerHome.html
- flask route: `/managerHome`
- data required:
    - `manager.name`
    - a list `projects` that includes the `name`, `id`, and a `riskinformation` string for each one

### createProject.html
- flask route: `/createProject`
- I haven't yet done the AJAX and JavaScript
- transmits all project-specific variables
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
- I haven't done the AJAX yet.
- data required: 
    - list of skills currently in the database for the developer, named `currentSkills`.

### softSkills.html
- flask route: `/softSkills`
- data required:
    - an `isManager` global (session) variable in flask (used for redirecting to  the correct home menu from the soft skills page)
    - a `defaultvalues` array with the 5 soft skill variables that are currently in the database

### logout.html
- flask route: /logout