import json, sys, os, time, datetime, math, random
import numpy as np
from housepy import config, log, util, strings, science
from point import Point

class City(object):
        
    def __init__(self, id, centroid):
        self.id = id
        self.centroid = centroid
        self.label = None
        self.places = []
        self.date_range = None
    
    def __str__(self):
        return "[%d] %s\t(%f,%f) <%s> - <%s> Places: [%s]" % (self.id, self.label, self.centroid.lat, self.centroid.lon, self.date_range[0], self.date_range[1], ','.join([str(place.id) for place in self.places]))
        
    def to_json(self):
        return self.label if self.label is not None else str(self.id)

    def calc_range(self):
        ts = [point.t for place in self.places for point in place.points]
        earliest = datetime.datetime.fromtimestamp(min(ts))
        latest = datetime.datetime.fromtimestamp(max(ts))
        self.date_range = earliest, latest


    @staticmethod    
    def find_cities(places, city_radius):

        vectors = []
        for place in places:
            vectors.append((place.centroid.lon, place.centroid.lat))

        ct = science.ClusterTree.build(vectors, science.geo_distance)
        # print("city clustertree:")
        # print(ct.draw())
        clusters = ct.get_pruned(city_radius)

        cities = [City(c, Point(None, cluster.vector[0], cluster.vector[1])) for (c, cluster) in enumerate(clusters)]

        def get_closest(place):
            min_d = float('inf')
            for cluster in clusters:
                d = science.geo_distance((place.centroid.lon, place.centroid.lat), cluster.vector)
                if d < min_d:
                    closest_cluster = cluster
                    min_d = d
            return closest_cluster        

        for place in places:
            city = cities[clusters.index(get_closest(place))]
            city.places.append(place)
            place.city = city
            for point in place.points:
                point.city = city

        for city in cities:
            city.calc_range()

        return cities

