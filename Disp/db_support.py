import pyodbc
import global_attributes as ga





def connect_to_db(name:str) -> bool:
    try:
        temp_conn  = pyodbc.connect("DSN=" + name)
        temp_cur = temp_conn.cursor()
        #temp_cur.fast_executemany = True
        ga.conn = temp_conn
        ga.cur = temp_cur
        return True
    except Exception:
        return False
    
def close_connection():
    if not ga.conn is None:
        ga.conn.close()







def upload_triggers(data) -> bool:
    sql = f"INSERT INTO temp_triggers(uci, trigger_date, trigger_type) VALUES (?, ?, ?)"
    ga.cur.executemany(sql, data)
    
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
    ga.cur.execute(sql)
    sql = "DELETE FROM temp_triggers"
    ga.cur.execute(sql)

    ga.cur.commit()

