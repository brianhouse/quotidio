import json, sys, os, time, datetime, math, random
from housepy import config, log, geo
from point import Point
from cluster_tree import ClusterTree

class Place(object):
        
    def __init__(self, id, centroid, color=(0.0, 0.0, 0.0, 1.0)):
        self.id = id
        self.label = None
        self.centroid = centroid
        self.color = color
        self.points = []
        self.paths = []
        self.connections = {}
        self.city = None
                        
    def graph(self):
        g = {}
        for place, strength in self.connections.items():
            g[place.id] = strength
        return {'id': self.id, 'connections': g}
    
    def __str__(self):
        return "[%d] %s\t(%f,%f) Connections: %s Points: [%s]" % (self.id, self.label, self.centroid.lat, self.centroid.lon, [place.id for place in self.connections], ','.join([str(point.id) for point in self.points]))
        
    def to_json(self):
        return self.label if self.label is not None else str(self.id)

    @staticmethod    
    def find_places(paths, cluster_radius):

        # get matrix of unique path terminal coordinates for our vector input
        terminals = []
        for path in paths:
            terminals.append(path.start_point)
            terminals.append(path.end_point)
        terminals = list(set(terminals))
        vectors = []
        for terminal in terminals:
            vectors.append((terminal.lon, terminal.lat))
            # print "%f, %f" % (terminal.lon, terminal.lat)

        ct = ClusterTree.build(vectors, geo.distance)
        # print("place clustertree:")
        # print(ct.draw())
        clusters = ct.get_pruned(cluster_radius)

        # initialize place
        def make_color(c):            
            return c, 1., 1.
        places = [Place(c, Point(None, cluster.vector[0], cluster.vector[1]), make_color(c / len(clusters))) for (c, cluster) in enumerate(clusters)]    # point is just convenience for centroid
        for place in places:
            place.centroid.normalize_position()
        
        # re-associate path terminals with clusters
        def get_closest(point):
            # in theory, a point in a cluster could be closer to the centroid of a different cluster (maybe?). however, I dont think doing things this way will be detrimental
            min_d = float('inf')
            for cluster in clusters:
                d = geo.distance((point.lon, point.lat), cluster.vector)
                if d < min_d:
                    closest_cluster = cluster
                    min_d = d
            return closest_cluster        

        for path in paths:
            path.start_place = places[clusters.index(get_closest(path.start_point))]
            path.end_place = places[clusters.index(get_closest(path.end_point))]
            path.start_place.points.append(path.start_point)
            path.end_place.points.append(path.end_point)              
            # skip paths that dont go anywhere
            if path.start_place == path.end_place:                
                for point in path:
                    point.moving = False
                    point.place = path.start_place
            else:
                # build connection graph            
                path.start_place.paths.append(path)
                if path.end_place in path.start_place.connections:
                    path.start_place.connections[path.end_place] += 1
                else:
                    path.start_place.connections[path.end_place] = 1    
                path.end_point.place = path.end_place

        # normalize connections and uniquify point lists
        max_points = max([len(place.points) for place in places])
        max_paths = max([max(place.connections.values()) if len(place.connections) else 0 for place in places])
        for place in places:
            for connection, weight in place.connections.items():
                place.connections[connection] = weight / float(max_paths)
            place.points = list(set(place.points))

        return places    
