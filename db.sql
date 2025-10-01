
CREATE TABLE trigger_types(
    id          BYTE PRIMARY KEY,
    name        TEXT(20)
);

INSERT INTO trigger_types(id, name) VALUES (0, 'Citizenship')
INSERT INTO trigger_types(id, name) VALUES (1, 'Deceased')
INSERT INTO trigger_types(id, name) VALUES (2, 'Departure')

CREATE TABLE triggers(
    uci            LONG,
    trigger_type   BYTE,
    trigger_date   DATE,
    PRIMARY KEY (uci, trigger_type, trigger_date),
    CONSTRAINT triggers1 FOREIGN KEY (trigger_type) REFERENCES trigger_types(id)
);

CREATE TABLE temp_triggers(
    uci            LONG,
    trigger_type   BYTE,
    trigger_date   DATE
);

-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --
-- |- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -| --
-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --


CREATE TABLE event_types(
    id          AUTOINCREMENT PRIMARY KEY,
    name        TEXT(50)
);

CREATE TABLE event_stages(
    id          AUTOINCREMENT PRIMARY KEY,
    name        TEXT(50)
);

CREATE TABLE events(
    id               LONG PRIMARY KEY,
    uci              LONG,
    event_type       INT,
    event_stage      INT,
    event_date       DATE,
    last_date        DATE,
    CONSTRAINT events1 FOREIGN KEY (event_type) REFERENCES event_types(id),
    CONSTRAINT events2 FOREIGN KEY (event_stage) REFERENCES event_stages(id)
);

CREATE TABLE temp_events(
    id               LONG,
    uci              LONG,
    event_type       TEXT(50),
    event_stage      TEXT(50),
    event_date       DATE,
    last_date        DATE
);

-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --
-- |- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -| --
-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --

CREATE TABLE locations(
    id          AUTOINCREMENT PRIMARY KEY,
    name        TEXT(100),
    is_offsite  YESNO,
    is_officer  YESNO,
    is_internal YESNO
);

CREATE TABLE offices(
    id           INT PRIMARY KEY,
    name         TEXT(100),
    is_internal  YESNO
);

CREATE TABLE projects(
    id           INT PRIMARY KEY,
    name         TEXT(100)
);

CREATE TABLE box_types(
    id          INT PRIMARY KEY,
    name        TEXT(100)    
);

CREATE TABLE box_stages(
    id         INT PRIMARY KEY,
    name       TEXT(100)
);

-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --
-- |- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -| --
-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --

CREATE TABLE boxes(
    id                        AUTOINCREMENT PRIMARY KEY,
    office                    INT,
    location                  LONG,

    project                   INT,
    box_type                  INT, --Practical Type
    box_subtype               INT, --Superficial Type

    name                      TEXT(50),
    stage                     INT,
    intended_destruction_date DATE,


    CONSTRAINT boxes1 FOREIGN KEY office REFERENCES offices(id),
    CONSTRAINT boxes2 FOREIGN KEY project REFERENCES project(id),
    CONSTRAINT boxes3 FOREIGN KEY stage REFERENCES box_stages(id),
    CONSTRAINT boxes4 FOREIGN KEY location REFERENCES locations(id),
    CONSTRAINT boxes5 FOREIGN KEY box_type REFERENCES box_types(id),
    CONSTRAINT boxes6 FOREIGN KEY box_subtype REFERENCES box_types(id)
);

CREATE TABLE dispositions(
    uci                       LONG,
    box                       LONG,
    volumes                   BYTE,
    volumes_temp              BYTE,
    last_event_date           DATE,
    intended_destruction_date DATE,

    PRIMARY KEY (uci, box),

    CONSTRAINT dispositions1 FOREIGN KEY box REFERENCES boxes(id) 

);









CREATE TABLE criminality_types(
    id          INT PRIMARY KEY,
    name        TEXT(50)
);

CREATE TABLE box_types(
    id          INT PRIMARY KEY,
    name        TEXT(50)
);

-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --
-- |- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -| --
-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --



CREATE TABLE storage_stages(
    id          INT PRIMARY KEY,
    name        TEXT(30)
);

-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --
-- |- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -| --
-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --

CREATE TABLE locations(
    id          INT PRIMARY KEY,
    name        TEXT(100),
    is_offsite  YESNO,
    is_officer  YESNO,
    is_internal YESNO
);

CREATE TABLE offices(
    id           INT PRIMARY KEY,
    name         TEXT(100),
    is_internal  YESNO
);

CREATE TABLE projects(
    id           INT PRIMARY KEY,
    name         TEXT(100)
);

-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --
-- |- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -| --
-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --











CREATE TABLE destruction_approvals(

);

CREATE TABLE box_removals(

);


CREATE TABLE boxes(

);

CREATE TABLE dispositions(

);



CREATE TABLE boxes(
    id          AUTOINCREMENT PRIMARY KEY,
    name        TEXT(20),
    location    LONG,
    office      INT,
    project     INT,
    box_type    BYTE,   --Having To Do With The Practial Contents (Defining Its Destruction, Use) 
    box_subtype BYTE,   -- Specifying Subclassifications Of Type (IE Year Range)
    intended_destruction_date
);


CREATE TABLE approvals(
    id            AUTOINCREMENT PRIMARY KEY,
    box           LONG,
    approval_date DATE,


);

















CREATE TABLE boxes(
    id                AUTOINCREMENT PRIMARY KEY,
    name              TEXT(20),
    location          LONG,
    office            LONG,
    project           BYTE,
    box_type          BYTE,
    destruction_date  DATE,
    destruction_stage BYTE,
    CONSTRAINT boxes1 FOREIGN KEY (location) REFERENCES locations(id),
    CONSTRAINT boxes2 FOREIGN KEY (office) REFERENCES offices(id),
    CONSTRAINT boxes3 FOREIGN KEY (box_type) REFERENCES box_types(id),
    CONSTRAINT boxes4 FOREIGN KEY (destruction_stage) REFERENCES destruction_stages(id)
);






CREATE TABLE dispositions(
    id               AUTOINCREMENT PRIMARY KEY,
    uci              LONG,
    box              LONG,
    main_vols        BYTE,
    temp_vols        BYTE,
    disposition_date DATE,
    starting_date    DATE,
    duration         BYTE,
    CONSTRAINT dispositions1 FOREIGN KEY (box) REFERENCES boxes(id)
);

-- |----------|---------|-------------|------------|-------------|-----------|-------------|
-- |- - - - - |- - - - -| - - - - - - |- - - - - - |- - - - - - -| - - - - - |- - - - - - -| -
-- |----------|---------|-------------|------------|-------------|-----------|-------------|


INSERT INTO destruction_stages(id, name) VALUES (0, 'Problematic')
INSERT INTO destruction_stages(id, name) VALUES (1, 'Prepared')
INSERT INTO destruction_stages(id, name) VALUES (2, 'Ready')
INSERT INTO destruction_stages(id, name) VALUES (3, 'Approved')
INSERT INTO destruction_stages(id, name) VALUES (4, 'Destroyed')


-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --
-- |- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -|- - - - - -| --
-- |-----------|-----------|-----------|-----------|-----------|-----------|-----------| --