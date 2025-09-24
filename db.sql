CREATE TABLE trigger_types(
    id          LONG PRIMARY KEY,
    label       TEXT(50)
);

CREATE TABLE offices(
    id         AUTOINCREMENT PRIMARY KEY,
    label      TEXT(50)
);

CREATE TABLE locations(
    id          AUTOINCREMENT PRIMARY KEY,
    label        TEXT(50),
    is_offsite     YESNO,
    is_officer     YESNO
);

CREATE TABLE event_types(
    id      AUTOINCREMENT PRIMARY KEY,
    label   TEXT(50)
);

CREATE TABLE event_stages(
    id      AUTOINCREMENT PRIMARY KEY,
    label   TEXT(50)
);

CREATE TABLE criminality_types(
    id     AUTOINCREMENT PRIMARY KEY,
    label  TEXT(50)
);


INSERT INTO trigger_types (id, label) VALUES (0, 'Citizenship');
INSERT INTO trigger_types (id, label) VALUES (1, 'Deceased');
INSERT INTO trigger_types (id, label) VALUES (2, 'Departure');

CREATE TABLE temp_triggers(
    uci LONG,
    trigger_date DATE,
    trigger_type LONG
);

CREATE TABLE triggers (
    uci          LONG,
    trigger_date DATE,
    trigger_type LONG,
    PRIMARY KEY (uci, trigger_date, trigger_type),
    CONSTRAINT triggers_trigger_type FOREIGN KEY (trigger_type) REFERENCES trigger_types(id)
);

CREATE TABLE temp_files(
    uci          LONG,
    volumes      BYTE,
    is_temp      TEXT(1),
    office       TEXT(100),
    location     TEXT(100)
);

CREATE TABLE files(
    id           AUTOINCREMENT PRIMARY KEY,
    uci          LONG,
    volumes      BYTE,
    is_temp      YESNO,
    office       LONG,
    location     LONG,
    CONSTRAINT files_offices FOREIGN KEY (office) REFERENCES offices(id),
    CONSTRAINT files_locations FOREIGN KEY (location) REFERENCES locations(id)
);


CREATE TABLE temp_events(
    uci         LONG,
    event_date  DATE,
    event_type  LONG,
    event_stage LONG
);




CREATE TABLE events(
    id          LONG PRIMARY KEY
    uci         LONG,
    event_date  DATE,
    event_type  LONG,
    event_stage LONG,
    CONSTRAINT events_event_type FOREIGN KEY (event_type) REFERENCES event_types(id),
    CONSTRAINT events_event_stage FOREIGN KEY (event_stage) REFERENCES event_stages(id)
);










CREATE TABLE boxes(
    id                 AUTOINCREMENT PRIMARY KEY,
    label              TEXT(30),
    destruction_date   DATE,
    status             LONG,




);




CREATE TABLE dispositions(
    id           AUTOINCREMENT PRIMARY KEY,
    uci          LONG,
    main_volumes LONG,
    temp_volumes LONG,

);




































CREATE TABLE box_types(
    id         LONG PRIMARY KEY,
    label      TEXT(50)
);


INSERT INTO box_types(id, label) VALUES (1, '');
INSERT INTO box_types(id, label) VALUES (2, '');
INSERT INTO box_types(id, label) VALUES (3, '');
INSERT INTO box_types(id, label) VALUES (4, '');
INSERT INTO box_types(id, label) VALUES (5, '');
INSERT INTO box_types(id, label) VALUES (6, '');




CREATE TABLE boxes(
    id                   AUTOINCREMENT PRIMARY KEY,
    label                TEXT(20),
    destruction_date     DATE,
    project              LONG,
    destruction_type     LONG,
    box_type             LONG,
    location             LONG,
    CONSTRAINT boxes_location FOREIGN KEY (location) REFERENCES offices(id),
    CONSTRAINT boxes_box_type FOREIGN KEY (box_type) REFERENCES box_types(id)
);





INSERT INTO box_types(id), label






















CREATE TABLE event_types(
    id            LONG PRIMARY KEY,
    label         TEXT(50)
);

INSERT INTO event_types(id, label)
VALUES (1, "Detention Hold")

CREATE TABLE event_stages(
    id            LONG PRIMARY KEY,
    label         TEXT(50)
);
INSERT INTO event_stages(id, label)
VALUES (1, "Concluded")

CREATE TABLE events(
    uci             LONG,
    start_date      DATE,
    event_type      INT,
    event_stage     INT,
    PRIMARY KEY (uci, start_date, event_type),
    CONSTRAINT events_type FOREIGN KEY (event_type) REFERENCES event_types(id)
);



CREATE TABLE boxes(
    id               LONG,
    [label]          TEXT(20),
    destruction_date DATE,
    [type]           INT,
    [location]       INT
);















CREATE TABLE criminality_types(
    id             LONG,
    [label]        TEXT(50),
    is_destroyable YESNO
)


CREATE TABLE dispositions(
    uci               LONG,
    [box]             TEXT(20),
    vols_main         INT,
    vols_temp         INT,
    destruction_date  DATE,
    is_destroyed         YESNO
);