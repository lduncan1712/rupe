CREATE TABLE trigger_types(
    id          LONG PRIMARY KEY,
    label       TEXT(50)
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
    CONSTRAINT triggers_type FOREIGN KEY (trigger_type) REFERENCES trigger_types(id)
);

















CREATE TABLE offices(
    id         LONG PRIMARY KEY,
    [label]    TEXT(50)
);

CREATE TABLE locations(
    id          LONG PRIMARY KEY,
    [label]     TEXT(50),
    is_offsite     YESNO
);

CREATE TABLE files(
    id          AUTOINCREMENT PRIMARY KEY,
    uci         LONG,
    vols        INT DEFAULT 0,
    is_temp     YESNO,
    [location]  INT,
    office      INT,
    CONSTRAINT files_uci FOREIGN KEY (uci) REFERENCES clients(uci),
    CONSTRAINT files_location FOREIGN KEY ([location]) REFERENCES locations(id),
    CONSTRAINT files_office FOREIGN KEY (office) REFERENCES offices(id)
);


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