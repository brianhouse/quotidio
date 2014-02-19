import json, sys, os, time, datetime, math, random
from housepy import config, log, geo
from point import Point
from cluster_tree import ClusterTree

class City(object):
        
    def __init__(self, id, centroid):
        self.id = id
        self.centroid = centroid
        self.label = None
        self.places = []
    
    def __str__(self):
        return "[%d] %s\t(%f,%f) Places: [%s]" % (self.id, self.label, self.centroid.lat, self.centroid.lon, ','.join([str(place.id) for place in self.places]))
        
    def to_json(self):
        return self.label if self.label is not None else str(self.id)

    @staticmethod    
    def find_cities(places, city_radius):

        vectors = []
        for place in places:
            vectors.append((place.centroid.lon, place.centroid.lat))

        ct = ClusterTree.build(vectors, geo.distance)
        # print("city clustertree:")
        # print(ct.draw())
        clusters = ct.get_pruned(city_radius)

        # print("clusters")
        # print(clusters)

        cities = [City(c, Point(None, cluster.vector[0], cluster.vector[1])) for (c, cluster) in enumerate(clusters)]
        for city in cities:
            city.centroid.normalize_position()

        def get_closest(place):
            min_d = float('inf')
            for cluster in clusters:
                d = geo.distance((place.centroid.lon, place.centroid.lat), cluster.vector)
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

        return cities

