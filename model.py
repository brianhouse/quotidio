import sqlite3, json, os
from housepy import log

connection = sqlite3.connect(os.path.abspath(os.path.join(os.path.dirname(__file__), "data.db")))
connection.row_factory = sqlite3.Row
db = connection.cursor()

def init():
    try:
        db.execute("CREATE TABLE IF NOT EXISTS data (t INTEGER, raw TEXT, derived TEXT)")
        db.execute("CREATE INDEX IF NOT EXISTS data_t ON data(t)")
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
init()

def insert(t, data):
    try:
        db.execute("INSERT INTO data (t, raw) VALUES (?, ?)", (t, data))
        entry_id = db.lastrowid
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
    log.info("Inserted feature (%s) %s" % (entry_id, t))    
    return entry_id