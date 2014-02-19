import json, sys, os, time, datetime, math, random
import numpy as np
from housepy import config, log, util, strings, geo
from point import Point

MOVING_THRESHOLD = 60 * 10    # if points are within 10 minutes, we are in transit
SPEED_TYPE = ['walk', 'bike', 'trans', 'drve']

class Path(list):

    def __init__(self, id):
        self.id = id
        self.start_place = None
        self.end_place = None
        self.speed_index = None
        
    def bake(self):    
        self.start_point = self[0]
        self.end_point = self[-1]  
        self.distance = geo.distance(self.start_point.location, self.end_point.location)      
        self.start_time = self[1].date if len(self) > 1 and not Path.linked(self[0], self[1]) else self[0].date    # dont use the start_point date as the path start_time if we've been at the start_point for awhile
        self.end_time = self[-1].date
        self.calc_speed()

    def calc_speed(self):
        segment_speeds = []

        # ignore the first point if it's not within the moving threshold
        points = self[1:] if len(self) > 1 and not Path.linked(self[0], self[1]) else self[:]

        # dont consider paths that we really didnt capture (aka teleporting)    
        if len(points) < 2:
            self.speed = None
            return

        # calc segment speeds    
        for i, point in enumerate(points[:-1]):
            next = points[i+1]
            d = geo.distance(point.location, next.location, True)
            t = abs(point.t - next.t)
            if t > 0.0:
                segment_speeds.append(d / t)
        
        # we are using the second-to-fastest segment, if possible, as the speed for this path. cars also go slow; by not using the fastest we're filtering subway travel.
        segment_speeds.sort()
        self.speed = None
        index = -2
        while self.speed is None and index <= 0:
            try:
                self.speed = segment_speeds[index] * 60 * 60    # mph
            except IndexError as e:
                index += 1    
                        
    def __str__(self):
        return "[%s] %s %s %fmi %s %s (%f,%f) -> (%f,%f) Connects: [%s -> %s] Points: [%s]" % (str(self.id).zfill(2), self.start_time, (self.end_time - self.start_time), self.distance, "%smph" % str(int(self.speed)).zfill(2) if self.speed else "-----", SPEED_TYPE[self.speed_index] if self.speed_index is not None else "----", self.start_point.lat, self.start_point.lon, self.end_point.lat, self.end_point.lon, (self.start_place.id if self.start_place is not None else " "), (self.end_place.id if self.end_place is not None else " "),','.join([str(point.id) for point in self]))

    def __repr__(self):
        return str(self.id)

    @staticmethod
    def linked(a, b):
        t_a = a.t if type(a) == Point else a
        t_b = b.t if type(b) == Point else b
        duration = abs(t_a - t_b)
        return duration <= MOVING_THRESHOLD

    @staticmethod
    def find_paths(points):

        paths = []    
        path = Path(0)

        def close_path(path):
            start_index = points.index(path[0]) # prepend the point previous to the first point, which is the real assumed start (so min points in a path is 2)
            if start_index > 0:
                start_point = points[start_index - 1]
                path.append(start_point)
                start_point.paths.append(path)                        
                path.sort(key=lambda p: p.t)
            if len(path) > 2:    
                for p in path[1:-1]:    # all points not start and end points are moving
                    p.moving = True    
            paths.append(path)                                                   

        for i, point in enumerate(points):          
            if len(path) and Path.linked(point, path[-1]):    # if we are linked to the last point in this path, add it
                path.append(point)
                point.paths.append(path)
            else:
                # if not, close out this path                                
                if len(path):                
                    close_path(path)
                # start a new path with the current point 
                path = Path(len(paths))
                path.append(point)    
                point.paths.append(path)
        if len(path):
            close_path(path)        
        
        for path in paths:
            path.bake()
        Path.assign_speed_indexes(paths)

        log.info("Paths found: %s" % len(paths))
        for point in points:
            if not len(point.paths):
                log.error("Orphan point: %s" % point)

        return paths        

    @staticmethod
    def assign_speed_indexes(paths, clusters=3):
        moving_paths = [path for path in paths if path.speed is not None]
        speeds = [path.speed for path in moving_paths]

        # # by clustering
        # km = science.KMeans(clusters)  # walk, bike, drive
        # speed_indexes = km.learn(speeds)
        # for p, path in enumerate(moving_paths):
        #     path.speed_index = speed_indexes[p]

        # manually
        for path in moving_paths:
            if path.speed > 24:
                path.speed_index = 3
            elif path.speed > 17:
                path.speed_index = 2
            elif path.speed > 4:
                path.speed_index = 1
            else:
                path.speed_index = 0
