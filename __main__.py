import json, sys, os, time, datetime, math, random, json, calendar
import numpy as np
from .housepy import config, log, util, strings, science, database
from .point import Point
from .path import Path
from .place import Place
from .city import City

CLUSTER_RADIUS = 0.5 # places are no bigger than this many miles
CITY_RADIUS = 10.0 # cities are no bigger than this many miles


db = database.Connection()

# points = Point.find_points(db, calendar.timegm(util.parse_date("2011-05-01").timetuple()), time.time())
points = Point.find_points(db, calendar.timegm(util.parse_date("2011-05-27").timetuple()), calendar.timegm(util.parse_date("2012-05-27").timetuple()))       # 2011-05-25 is when OP began
paths = Path.find_paths(points)
places = Place.find_places(paths, CLUSTER_RADIUS)
cities = City.find_cities(places, CITY_RADIUS)

print()
print("POINTS")
for point in points:
    print(point)
print()     

print("PATHS")
for path in paths:
    print(path)        
print()    

print("PLACES")        
for place in places:
    print(place)  
print()          

print("CITIES")
for city in cities:
    print(city)
print()          


current_point = points[-1]
print("CURRENT")
if current_point.moving:
    print("--> moving")
else:
    print("Point: %s" % current_point)
    print("City: %s" % current_point.city)
    print("Place: %s" % current_point.place)
    print()
    print("NEXT PLACE")
    total_weight = sum([weight for place, weight in list(current_point.place.connections.items())])
    for place, weight in list(current_point.place.connections.items()):
        print(("%s (%d%%)" % (place.id, int((weight / total_weight) * 100.0))))

for point in points:
    place = point.place.id if point.place is not None else -1    
    city = point.city.id if point.city is not None else -1   
    derived = {'place': place, 'city': city}
    db.execute("UPDATE data SET derived=%s WHERE id=%s", json.dumps(derived), point.id)

