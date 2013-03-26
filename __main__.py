#!/usr/bin/env python

import json, sys, os, time, datetime, math, random, pickle
import numpy as np
from housepy import config, log, util, strings, science, drawing, database, net, util
from point import Point
from path import Path
from place import Place
from city import City
from almanac import Almanac
import geograph, tempograph, calegraph
    

if len(sys.argv) < 2:
    print("[filename]")
    exit()

log.info("Parsing OpenPaths file...")
path = os.path.abspath(os.path.expanduser(sys.argv[1]))
s = open(path).read()
data = json.loads(s)

center = -73.902615, 40.776243  # nyc
# center = -73.959486, 40.685193  # brooklyn
# center = -72.723889, 43.173611  # vermont       # no points!
# center = -71.009755, 41.569593  # new bedford
# center = -93.219539, 44.933524  # minneapolis
# center = -77.059081, 38.948266  # dc
# center = -104.890219, 39.698841 # denver
# center = -83.961412, 35.935478  # knoxville
# center = -73.490419, 41.908486  # berkshires
# center = -74.035318, 41.498944  # hudson valley
# center = 127.032687, 37.635063  # seoul
# center = -71.221729, 42.306461  # boston
# center = -68.700278, 45.658056  # millinocket
# center = -118.334105, 34.045948 # LA

# almanac = Almanac.build(data, time.mktime(util.parse_date('2011-05-25').timetuple()), time.mktime(util.parse_date('2012-05-27').timetuple()), center)
almanac = Almanac.build(data, time.mktime(util.parse_date('2011-08-01').timetuple()), time.mktime(util.parse_date('2012-05-27').timetuple()), center)
# almanac = Almanac.build(data, time.mktime(util.parse_date('2012-01-01').timetuple()), time.mktime(util.parse_date('2012-05-27').timetuple()), center)

print
print "POINTS"
print np.array(almanac.points)
print     

print "PATHS"
for path in almanac.paths:
    print path        
print    

print "PLACES"        
for place in almanac.places:
    print place  
print          

print "CITIES"        
for city in almanac.cities:
    print city
print          

print "CURRENT"
if almanac.current_point.moving:
    print "--> moving"
else:
    print almanac.current_point.city
    print almanac.current_point.place
    total_weight = sum([weight for place, weight in almanac.current_point.place.connections.items()])
    for place, weight in almanac.current_point.place.connections.items():
        print("%s (%f)" % (place.id, (weight / total_weight)))

# calegraph.draw(almanac[2012][1], brightness=0.33)
# calegraph.draw(almanac[2012][2])
# tempograph.draw(almanac.days)    

for city in almanac.cities:
    geograph.draw(city)    
    


