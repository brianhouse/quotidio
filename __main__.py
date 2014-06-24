#!/usr/bin/env python3

import json, sys, os, time, datetime, math, random, json
from housepy import config, log, util
from point import Point
from path import Path
from place import Place
from city import City

def process(filename, start_date="2000-01-01", end_date="2020-01-01"):

    log.info("Loading %s" % filename)
    path = os.path.abspath(os.path.expanduser(filename))
    with open(path) as f:
        s = f.read()
    data = json.loads(s)                
    log.info("DONE")

    # we're going to pretend OpenPaths timestamps are UTC
    # who knows what they actually are

    points = Point.find_points(data, util.timestamp(util.parse_date(start_date)), util.timestamp(util.parse_date(end_date)))
    paths = Path.find_paths(points)
    places = Place.find_places(paths, config['cluster_radius'])
    cities = City.find_cities(places, config['city_radius'])

    if config['verbose']:
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

    result = []
    for point in points:
        place = point.place.id if point.place is not None else -1    
        city = point.city.id if point.city is not None else -1   
        result.append({'place': place, 'city': city, 't': point.t})

    filename = "%s_quotidio.json" % filename.split('.')[0]
    with open(filename, 'w') as f:
        f.write(json.dumps(result, indent=4))

    return cities


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("[filename]")
        exit()

    cities = process(sys.argv[1])

    import geograph
    for city in cities:
        geograph.draw(city)
