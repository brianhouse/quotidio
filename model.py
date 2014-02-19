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
    log.info("Inserted point (%s) %s" % (entry_id, t))    
    return entry_id

def update(point_id, derived):
    try:
        db.execute("UPDATE data SET derived=? WHERE rowid=?", (json.dumps(derived), point_id))
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
    # log.info("Processed point (%s)" % point_id)

def fetch(start, end):
    db.execute("SELECT rowid as id, t, raw FROM data WHERE t>=? AND t<=? ORDER BY t", (start, end))
    return [dict(row) for row in db.fetchall()]
