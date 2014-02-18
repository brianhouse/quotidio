#!/usr/bin/env python

import time, urllib, urllib2, urlparse, datetime, sys, os, oauth2, json, calendar
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from housepy import strings, log, util, config, database, process          

process.secure_pid(os.path.join(os.path.dirname(__file__), "..", "run"))

if len(sys.argv) < 2:
    print("[filename]")
    exit()

path = os.path.abspath(os.path.expanduser(sys.argv[1]))
s = open(path).read()
data = json.loads(s)

db = database.Connection()
            
for d in data:
    try:
        data = json.dumps({'date': str(datetime.datetime.fromtimestamp(d['t'])), 'lon': d['lon'], 'lat': d['lat'], 'alt': d['alt']})
        db.execute("INSERT INTO data (source, t, raw) VALUES (%s, %s, %s)", 'openpaths', d['t'], data)
    except database.Duplicate:
        pass
    except Exception as e:
        log.error(log.exc(e))    

log.info("DONE")

