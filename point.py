import json, sys, os, time, datetime, math, random, calendar
import numpy as np
from housepy import config, log, util, strings, science


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
        self.x, self.y = science.geo_project((self.lon, self.lat))
        self.paths = []    
        self.place = None
        self.city = None
        self.moving = False
        TimedDatum.__init__(self, t)        
        
    @property
    def location(self):
        return self.lon, self.lat
                
    def __str__(self):
        return "[%s] %s (%f,%f) %s %s%s" % (str(self.id).zfill(2), self.date, self.lat, self.lon, ("moving" if self.moving else ""), ("%s:" % self.city.id if self.city is not None else ""), (self.place.id if self.place is not None else "")) 

    def __repr__(self):
        return "(%f, %f, %s)" % (self.lat, self.lon, self.date)
