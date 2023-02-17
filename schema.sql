DROP TABLE IF EXISTS Projects;
DROP TABLE IF EXISTS Project_Requirement;
DROP TABLE IF EXISTS Project_Risk;
DROP TABLE IF EXISTS Time_Component;
DROP TABLE IF EXISTS Cost_Component;
DROP TABLE IF EXISTS Project_Managers;
DROP TABLE IF EXISTS Developers;
DROP TABLE IF EXISTS Developer_Project;
DROP TABLE IF EXISTS Developer_Strength;

-- what happens if a project_manager is fired? is it really feasible that the project has to be deleted?
CREATE TABLE Projects (
    -- Primary and Foreign keys
    project_id SERIAL INT PRIMARY KEY,

    project_manager_id INT NOT NULL REFERENCES Project_Managers(project_manager_id) ON DELETE CASCADE,

    -- Fields
    project_name VARCHAR(255) NOT NULL,
    
    deadline INT NOT NULL
    CONSTRAINT deadline_nonnegative CHECK (deadline>=0),

    budget INT NOT NULL
    CONSTRAINT budget_nonnegative CHECK (budget>=0),

    state VARCHAR(20) NOT NULL
    CONSTRAINT project_state_ok CHECK (state in ('Success','Failure','Ongoing','Cancelled'))
);

CREATE TABLE Project_Requirement (
    -- Primary and Foreign keys
    requirement_id SERIAL INT PRIMARY KEY,

    project_id INT NOT NULL REFERENCES Project(project_id) ON DELETE CASCADE,

    -- Fields
    requirement varchar(255) NOT NULL
);

CREATE TABLE Project_Risk (
    -- Primary and Foreign keys
    project_risk_id SERIAL INT PRIMARY KEY,

    project_id INT NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE,

    -- Fields
    monte_carlo_time INT,

    monte_carlo_cost INT,

    state NOT NULL
    CONSTRAINT project_risk_state_ok CHECK (state in ('Green','Amber','Red'))
);

CREATE TABLE Time_Component (
    -- Primary and Foreign keys
    time_component_id SERIAL INT NOT NULL,

    project_risk_id INT NOT NULL REFERENCES Project_Risk(project_risk_id) ON DELETE CASCADE,

    -- Fields
    best INT,

    worst INT,

    average INT,

    absolute_value INT
);

CREATE TABLE Cost_Component (
    -- Primary and Foreign keys
    cost_component_id SERIAL INT NOT NULL,

    project_risk_id INT NOT NULL REFERENCES Project_Risk(project_risk_id) ON DELETE CASCADE,

    -- Fields
    best INT,

    worst INT,

    average INT,

    absolute_value INT
);

CREATE TABLE Project_Managers (
    -- Primary key
    project_manager_id SERIAL INT PRIMARY KEY,

    -- Fields
    first_name VARCHAR(255) NOT NULL,

    last_name VARCHAR(255) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    enthusiasm INT,

    purpose INT,

    challenge INT,

    health INT,

    resilience INT
);

CREATE TABLE Developers (
    -- Primary key
    developer_id SERIAL INT PRIMARY KEY,

    -- Fields
    first_name VARCHAR(255) NOT NULL,

    last_name VARCHAR(255) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    enthusiasm INT,

    purpose INT,

    challenge INT,

    health INT,

    resilience INT
);

CREATE TABLE Developer_Project (
    -- Foreign keys
    developer_id INT NOT NULL REFERENCES Developers(developer_id) ON DELETE CASCADE,

    project_id INT NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE
);

CREATE TABLE Developer_Strength (
    -- Primary and Foreign keys
    strength_id SERIAL INT PRIMARY KEY,

    developer_id INT NOT NULL REFERENCES Developers(developer_id) ON DELETE CASCADE,

    -- Field
    strength varchar(255)

);



-- Foreign keys manually enabled on initialisation
PRAGMA foreign_keys = ON;

-- needs testing

-- to run:
-- go to directory with this file.
-- command line:
-- sqlite3 cs261.db < schema.sql