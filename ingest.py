#!/usr/bin/env python3

import sys, os, json, datetime, model
from housepy import log

if len(sys.argv) < 2:
    print("[filename]")
    exit()

path = os.path.abspath(os.path.expanduser(sys.argv[1]))
s = open(path).read()
data = json.loads(s)
            
for d in data:
    data = json.dumps({'date': str(datetime.datetime.fromtimestamp(d['t'])), 'lon': d['lon'], 'lat': d['lat']})
    model.insert(d['t'], data)

log.info("DONE")

