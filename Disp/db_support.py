import pyodbc
import global_attributes as ga






def connect_to_db(name:str) -> bool:
    try:
        temp_conn  = pyodbc.connect("DSN=" + name)
        temp_cur = temp_conn.cursor()

        ga.conn = temp_conn
        ga.cur = temp_cur

        return True
    except Exception:
        return False
    
def close_connection():
    if not ga.conn is None:
        ga.conn.close()

def get_primary_keys(table:str) -> list:
    pk_info = ga.cur.primaryKeys(table=table)
    pk_name = pk_info.column_name
    ga.cur.execute(f"SELECT {pk_name} FROM {table}")
    primary_keys = {row[0] for row in ga.cur.fetchall()}
    ga.cur.close()
    return primary_keys


def row_generator(d:dict):
    for k,v in d.items():
        yield (k, *v)    



def upload_triggers(trigger:int, data:list):

    #INSERT UNIQUE COMBOS INTO TEMP TRIGGERS
    ga.cur.executemany("INSERT INTO temp_triggers(uci,date,type) VALUES (?,?,?)", data)
    
    #CREATE NEW INDIVIDUALS
    ga.cur.execute("""
                       INSERT INTO clients(uci)
                       SELECT temp_triggers.uci
                       FROM temp_triggers
                       LEFT JOIN clients
                       ON temp_triggers.uci = clients.uci
                       WHERE clients.uci IS NULL,
                       """)
    
    #CREATE NEW TRIGGERS
    ga.cur.execute("""
                       INSERT INTO triggers(uci, date, type)
                       SELECT uci, date, type FROM temp_triggers
                       """)
    
    #CLEAR TEMP TABLE
    ga.cur.execute("DELETE FROM temp_triggers")



def upload_files():


    #UCI, OFFICE, VOLUMES, IS_TEMP
    pass

def upload_bsfs():

    ga.cur.execute("""
                   INSERT INTO temp_file_disposition()
                   
                   """)

    #OFFICE, UCI, VOLUMES, TEMP_VOLUMES

def upload_events():

    #UCI, TYPE, START, STAGE
    pass







def upload_project_files(do_clear:bool, d:dict, trigger:int):

    if trigger == 0:
        trigger_col = "TRIGGER_CIT"
    elif trigger == 1:
        trigger_col = "TRIGGER_DEC"
    elif trigger == 2:
        trigger_col = "TRIGGER_DEP"
    
    ga.cur.executemany("INSERT INTO TEMP_TRIGGER (UCI,TRIGGER_DATE,CRIMINALITY) VALUES (?,?,?)", row_generator(d))

    ga.cur.execute(""" 
                    UPDATE files
                    INNER JOIN TEMP_TRIGGER
                    ON files.uci = TEMP_TRIGGER.uci
                    SET
                    files.{trigger_col} = True
                    files.CRIMINALITY = TEMP_TRIGGER.CRIMINALITY
                    files.TRIGGER_LATEST = IIF(files.TRIGGER_LATEST > TEMP_TRIGGER.TRIGGER_DATE,
                                                files.TRIGGER_LATEST,
                                                TEMP_TRIGGER.TRIGGER_DATE)
                   """)
    
    ga.cur.execute("""
                   INSERT INTO files(uci, {trigger_col}, TRIGGER_LATEST, CRIMINALITY)
                   SELECT TEMP_TRIGGER.uci, True, TEMP_TRIGGER.TRIGGER_DATE, TEMP_TRIGGER.CRIMINALITY
                   FROM TEMP_TRIGGER
                   LEFT JOIN FILES
                   ON TEMP_TRIGGER.UCI = FILES.UCI
                   WHERE files.UCI IS NULL
                   """)
    
    ga.cur.execute("DELETE FROM TEMP_TRIGGER")
    
    ga.conn.commit()





def upload_bsf_files(do_clear:bool, d:dict, is_hold:bool, destruction_year:int, is_fill:bool):
    
    #INPUT TEMP-BSF
    ga.cur.executemany("INSERT INTO TEMP_BSF (UCI,BOX,DESTRUCTION) VALUES (?,?,?)")

    #INPUT TEMP-BOXES
    ga.cur.execute("""
                   INSERT INTO TEMP_BOX (BOX) SELECT DISTINCT BOX FROM TEMP_BSF
                   """)
    
    #CRAETE NEW BOXES
    ga.cur.execute("""
                   INSERT INTO BOX(BOX,YEAR,HAS_HOLD,IS_FILL)
                   SELECT TEMP_BOX.BOX,{destruction_year},{is_hold},{is_fill} FROM TEMP_BOX
                   LEFT JOIN BOX
                   ON TEMP_BOX.BOX = BOX.BOX
                   WHERE BOX.BOX IS NULL;
                   """)

    #UPDATE EXISTING
    ga.cur.execute("""
                   UPDATE BOX
                   INNER JOIN TEMP_BOX
                   ON BOX.BOX = TEMP_BOX.BOX
                   SET
                        BOX.destruction_year = {destruction_year}
                        BOX.is_hold = {is_hold}
                        BOX.is_fill = {is_fill}
                   """)
    
    #CREATE
    ga.cur.execute("""
                   INSERT INTO FILES(UCI, BSF_BOX, BFS_DESTRUCTION, BSF_IS_HOLD)
                   SELECT TEMP_BSF.UCI, TEMP_BSF.BSF_BOX, TEMP_BSF.BSF_DESTRUCTION, {is_hold}
                   FROM TEMP_BSF 
                   LEFT JOIN FILES
                   ON TEMP_BSF.UCI = FILES.UCI
                   WHERE FILES.UCI IS NULL
                   """)
    
    #UPDATE
    ga.cur.execute("""
                   UPDATES FILES
                   INNER JOIN TEMP_BSF 
                   ON FILES.UCI = TEMP_BSF.UCI
                   SET
                    FILES.BSF_BOX = TEMP_BSF.BOX
                    FILES.BSF_IS_HOLD = {is_hold}
                    FILES.BSF_DESTRUCTION = TEMP_BSF.DESTRUCTION
                   """)
    

    
    
    






    #JOIN EXISTING
    ga.cur.executemany("""
                       UPDATES FILES
                       INNER JOIN TEMP_BSF
                       ON FILES.UCI = TEMP_BSF.UCI
                       SET
                            FILES.BSF_BOX = TEMP_BSF.BOX
                            FILES.BSF_DESTRUCTION = TEMP_BSF.DESTRUCTION
                            FILES.BSF_HAS_HOLD = {has_hold}
                        
                       """)
    
    #HANDLE NOT FOUND




    ga.cur.execute("""
    INSERT INTO FILES (UCI, BOX, DESTRUCTION)
    SELECT t.UCI, t.BOX, t.DESTRUCTION
    FROM TEMP_BSF AS t
    LEFT JOIN FILES AS f
        ON t.UCI = f.UCI AND t.BOX = f.BOX
    WHERE f.UCI IS NULL
    """)

    # 2. Update rows that already exist
    ga.cur.execute("""
    UPDATE FILES AS f
    INNER JOIN TEMP_BSF AS t
        ON f.UCI = t.UCI AND f.BOX = t.BOX
    SET f.DESTRUCTION = t.DESTRUCTION   
    """)

    # ✅ Commit once after both
    ga.conn.commit()

    #ADD THOSE THAT DONT EXIST

    #MODIFY THOSE THAT DO




    #LOAD INTO TEMP TABLE
    #ASSIGN BOXES








def upload_file_locations():
    pass

def upload_checklists():
    pass

