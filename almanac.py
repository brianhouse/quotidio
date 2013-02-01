import json, sys, os, time, datetime, math, random
import numpy as np
from housepy import config, log, util, strings, science
from point import Point
from path import Path
from place import Place
from city import City

RADIUS = 10.0
CLUSTER_RADIUS = 0.5 # places are no bigger than this many miles
CITY_RADIUS = 10.0 # cities are no bigger than this many miles

# special nyc version
RADIUS = 30.0
CITY_RADIUS = 30.0 # cities are no bigger than this many miles


class Almanac(dict):

    db = None

    def __init__(self, points, paths, places, cities):
        self.points = points
        self.paths = paths
        self.places = places
        self.cities = cities
        self.current_point = points[-1]
        years = {}
        for p, point in enumerate(reversed(points)):    # start with the most recent point
            if point.year not in years:
                years[point.year] = [[[None] * 1440 for d in xrange(7)] for w in xrange(52)]   # every minute in every day in every week
            year = years[point.year]    
            w = point.week    
            d = point.weekday
            m = point.minute
            while year[w][d][m] is None:
                year[w][d][m] = point.place if point.place is not None else -1  # flag for moving. might replace this with a speed / transportation mode indicator.
                if p == 0: # dont do it for the last point
                    break
                m += 1
                if m == len(year[w][d]):  # end of the day
                    m = 0
                    d += 1
                    if d == len(year[w]):   # end of the week
                        d = 0
                        w += 1
                        if w == len(year):  # end of the year
                            log.info("HIT END")
                            break
        dict.__init__(self, years)

    # def label(self):
    #     log.info("--> assigning labels")
    #     labels = Almanac.db.query("SELECT * FROM labels WHERE user_id=%s ORDER BY created", self.user_id)
    #     for label in labels:
    #         ## these time assignments should have a method
    #         d = label.created            
    #         minute = (d.hour * 60) + d.minute  # 5-minute period in the day, 0-indexed
    #         weekday = (d.weekday() + 1) % 7  # day of the week, 0=sunday
    #         week = d.isocalendar()[1] - 1    # week of the year, 0-indexed
    #         if weekday == 0:   # fix sundays (euros like to start on monday)
    #             week = (week + 1) % 52
    #         year = d.year
    #         place = self[year][week][weekday][minute]
    #         log.debug(place)
    #         if place is not None:
    #             log.info("--> labeled place %s as %s" % (place.id, label.label))
    #             place.label = label.label

    @staticmethod
    def is_empty(l):
        for e in l:
            if e is not None:
                return False
        return True

    @property
    def days(self):        
        days = []
        for y, year in self.items():
            for week in year:
                for day in week:
                    days.append(day)
        days = [day for day in days if not Almanac.is_empty(day)] # purges empty days for better-looking tempograph
        return days

    @property
    def current_week(self):
        now = datetime.datetime.now()
        year = now.year
        week = now.isocalendar()[1] - 1
        log.debug("Current year: %s" % year)
        log.debug("Current week: %s" % week)
        try:
            current_week = self[year][week]
        except Exception:
            log.debug("Week not found")
        else:
            return current_week

    @classmethod
    def build(cls, data, start, end, center=None):
        
        log.info("Loading OpenPaths data...")

        if center is not None:
            points = [Point(i, float(d['lon']), float(d['lat']), d['t']) for i, d in enumerate(data) if d['t'] >= start and d['t'] <= end and science.geo_distance((float(d['lon']), float(d['lat'])), center) <= RADIUS]            
        else:
            points = [Point(i, float(d['lon']), float(d['lat']), d['t']) for i, d in enumerate(data) if d['t'] >= start and d['t'] <= end]                        
        points.sort(key=lambda p: p.t)                

        log.info("Generating graph...")
        start_clock = time.clock()  


        paths = Path.find_paths(points)
        places = Place.find_places(paths, CLUSTER_RADIUS)  
        cities = City.find_cities(places, CITY_RADIUS)
        almanac = Almanac(points, paths, places, cities)

        # almanac.label()        

        print("(%ss)" % (time.clock() - start_clock))

        return almanac

