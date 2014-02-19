#!/usr/bin/env python3

import json, sys, os, time, datetime, math, random, json, model
from housepy import config, log, util
from point import Point
from path import Path
from place import Place
from city import City

CLUSTER_RADIUS = 0.5 # places are no bigger than this many miles
CITY_RADIUS = 10.0 # cities are no bigger than this many miles


def ingest(filename):
    path = os.path.abspath(os.path.expanduser(filename))
    s = open(path).read()
    data = json.loads(s)                
    for d in data:
        data = json.dumps({'lon': d['lon'], 'lat': d['lat']})
        model.insert(d['t'], data)
    log.info("DONE")


def process(start_date, end_date):

    # we're going to pretend OpenPaths timestamps are UTC
    # who knows what they actually are

    points = Point.find_points(util.timestamp(util.parse_date(start_date)), util.timestamp(util.parse_date(end_date)))
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
        model.update(point.id, derived)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("[filename] or [start_date] [end_date]")
    elif len(sys.argv) == 2:
        ingest(sys.argv[1])
    else:
        start_date, end_date = sys.argv[1], sys.argv[2]
        process(start_date, end_date)

