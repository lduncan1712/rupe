import pyodbc


conn = None
cur = None





def connect_to_db(name:str) -> bool:
    try:
        global conn
        global cur
        temp_conn  = pyodbc.connect("DSN=" + name)
        temp_cur = temp_conn.cursor()
        temp_cur.fast_executemany = True
        conn = temp_conn
        cur = temp_cur
        return True
    except Exception:
        return False
    
def close_connection():
    if not conn is None:
        conn.close()









def upload_triggers(data) -> bool:

    sql = "DELETE FROM temp_triggers"
    cur.execute(sql)

    sql = f"INSERT INTO temp_triggers(uci, trigger_date, trigger_type) VALUES (?, ?, ?)"
    cur.executemany(sql, data)
    
    sql = """
        INSERT INTO triggers(uci, trigger_date, trigger_type)
        SELECT t.uci, t.trigger_date, t.trigger_type
        FROM temp_triggers AS t
        WHERE NOT EXISTS (
            SELECT 1
            FROM triggers as trg
            WHERE trg.uci =          t.uci
            AND   trg.trigger_date = t.trigger_date
            AND   trg.trigger_type = t.trigger_type
        )
    """
    cur.execute(sql)
    cur.commit()


def upload_files(data) -> bool:
    
    sql = "DELETE FROM temp_files"
    cur.execute(sql)

    sql = f"INSERT INTO temp_files(uci, volumes, is_temp, office, location) VALUES (?, ?, ?, ?, ?)"
    cur.executemany(sql, data)

    sql = """
        INSERT INTO locations (label)
        SELECT DISTINCT t.location
        FROM temp_files AS t
        LEFT JOIN locations AS l
        ON t.location = l.label
        WHERE l.label IS NULL AND t.location IS NOT NULL;
    """
    cur.execute(sql)

    sql = """
        INSERT INTO offices (label)
        SELECT DISTINCT t.office
        FROM temp_files AS t
        LEFT JOIN offices AS o
        ON t.office = o.label
        WHERE o.label IS NULL AND t.office IS NOT NULL;
    """
    cur.execute(sql)

    sql = """
        INSERT INTO files(uci, volumes, is_temp, office, location)
        SELECT
            t.uci,
            t.volumes,
            IIF(t.is_temp = 'T', -1, 0),
            o.id As office,
            l.id As location
        FROM (temp_files As t
             INNER JOIN offices As o ON t.office = o.label)
             INNER JOIN locations As l ON t.location = l.label;
    """
    cur.execute(sql)
    cur.commit()


def upload_events(data) -> bool:

    sql = "DELETE FROM temp_events"
    cur.execute(sql)

    sql = f"INSERT INTO temp_events(id, uci, event_type, event_date, event_stage) VALUES (?,?,?,?,?)"
    cur.executemany(sql, data)

    sql = """
        INSERT INTO event_types(label)
        SELECT DISTINCT t.event_type
        FROM temp_events AS t
        LEFT JOIN event_types AS e
        ON t.event_type = e.label
        WHERE e.label IS NULL AND t.event_type IS NOT NULL;
        """
    cur.execute(sql)

    sql = """
        INSERT INTO event_stages(label)
        SELECT DISTINCT t.event_stage
        FROM temp_events AS t
        LEFT JOIN event_stages AS e
        ON t.event_stage = e.label
        WHERE e.label IS NULL AND t.event_stage IS NOT NULL;

    """
    cur.execute(sql)


    sql = """   
        UPDATE (events AS e
        INNER JOIN temp_events AS t ON e.id = t.id)
        INNER JOIN event_stages AS es ON t.event_stage = es.label
        SET e.event_stage = es.id;
    """
    cur.execute(sql)

    sql = """
        INSERT INTO events(id, uci, event_type, event_date, event_stage)
        SELECT 
            t.id,
            t.uci,
            et.id,
            t.event_date,
            es.id
        FROM ((temp_events AS t
            INNER JOIN event_types AS et ON t.event_type = et.label)
            INNER JOIN event_stages AS es ON t.event_stage = es.label)
            LEFT JOIN events AS e ON t.id = e.id
        WHERE e.id IS NULL;
    """
    cur.execute(sql)

    cur.commit()



