import json, sys, os, time, datetime, math, random
import numpy as np
from housepy import config, log, geo, util


class TimedDatum(object):

    def __init__(self, t=None):
        self.t = t
        if self.t is not None:
            self.date = datetime.datetime.utcfromtimestamp(self.t)
            self.minute = (self.date.hour * 60) + self.date.minute  # 5-minute period in the day, 0-indexed
            self.day = self.date.timetuple()[-2] - 1    # day of the year, 0-indexed
            self.weekday = (self.date.weekday() + 1) % 7  # day of the week, 0=sunday
            self.week = self.date.isocalendar()[1] - 1    # week of the year, 0-indexed
            if self.weekday == 0:   # fix sundays (euros like to start on monday)
                self.week = (self.week + 1) % 52
            self.month = self.date.month - 1    # month, 0-indexed
            self.year = self.date.year


class Point(TimedDatum):

    def __init__(self, id, lon, lat, t=None):
        self.id = id
        self.lon = lon
        self.lat = lat
        self.x, self.y = geo.project((self.lon, self.lat))
        self.paths = []    
        self.place = None
        self.city = None
        self.moving = False
        self.date = None
        TimedDatum.__init__(self, t)        
        
    @property
    def location(self):
        return self.lon, self.lat
        
    def normalize_position(self):
        self.x = util.scale(self.x, Point.min_x, Point.max_x)
        self.y = util.scale(self.y, Point.min_y, Point.max_y)                            
        
    def __str__(self):
        return "[%s] %s (%f,%f) %s %s%s" % (str(self.id).zfill(2), self.date, self.lat, self.lon, ("moving" if self.moving else ""), ("%s:" % self.city.id if self.city is not None else ""), (self.place.id if self.place is not None else "")) 

    def __repr__(self):
        return "(%f, %f, %s)" % (self.lat, self.lon, self.date)

    @classmethod
    def find_points(cls, results, start, end):

        points = []
        for i, data in enumerate(results):
            points.append(Point(i, float(data['lon']), float(data['lat']), float(data['t'])))

        lons = np.array([point.lon for point in points])
        lats = np.array([point.lat for point in points])
        xs = np.array([point.x for point in points])
        ys = np.array([point.y for point in points])
        cls.max_lon = np.max(lons)
        cls.min_lon = np.min(lons)
        cls.max_lat = np.max(lats)
        cls.min_lat = np.min(lats)
        cls.max_x = np.max(xs)
        cls.min_x = np.min(xs)
        cls.max_y = np.max(ys)
        cls.min_y = np.min(ys)
        points = list(points)
        for point in points:
            point.normalize_position()
            
        points.sort(key=lambda p: p.t)                

        log.info("%d points" % len(points))    

        return points

