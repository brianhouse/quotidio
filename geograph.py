import json, sys, os, time, datetime, math, random
from housepy import config, log, util, strings, science, drawing, net
from point import Point

# 12" at 72dpi is 864
# 12" at 300dpi is 3600
# cloudmade max is 2000x2000, which is 166.66dpi
# although we're really probably looking at a 10" square
# so 10" at 200dpi is 2000. going with that.

# 13-02-12 round 2
#
# for the small cities:
# 3in * 720dpi = 2160 pixels square
# 1pt = (1/0.75)px @ 72dpi
# 1pt = (10/0.75)px @ 720dpi = 1/0.075 ~ 13.33px, call it 15px
#
# for the small cities:
# 12in * 720dpi = 8640 pixels square
# 1pt = (1/0.75)px @ 72dpi
# 1pt = (10/0.75)px @ 720dpi = 1/0.075 ~ 13.33px, call it 15px


SIZE = 2160, 2160
SIZE = 8640, 8640

def draw(city):

    print
    print "DRAWING CITY %s %s,%s" % (city.id, city.centroid.lat, city.centroid.lon)

    places = city.places

    if len(places) < 5:
        print("Too few places")
        return
    
    points = [point for place in places for point in place.points]
    print points

    upper_left = Point(-1, max([point.lon for point in points]), min([point.lat for point in points]))
    lower_right = Point(-1, min([point.lon for point in points]), max([point.lat for point in points]))

    normalize_points(points + [place.centroid for place in places] + [city.centroid] + [upper_left, lower_right])

    def get_ctl(x, y, length, slope):
        return length * math.cos(math.atan(slope)) + x, length * math.sin(math.atan(slope)) + y    

    ctx = drawing.Context(SIZE[0], SIZE[1], relative=True, flip=True, hsv=True, margin=100, background=(0., 0., 1., 1.))    

    for place in places:

        # # draw clusters
        # for i, point in enumerate(place.points):
        #     ctx.line(point.x, point.y, place.centroid.x, place.centroid.y, stroke=place.color)
        #     ctx.arc(point.x, point.y, 3 / 1000.0, thickness=0.0, fill=place.color)   

        # draw place connections    
        for connection, weight in place.connections.items():
            if connection not in places:
                continue
            # straight line
            # ctx.line(place.centroid.x, place.centroid.y, connection.centroid.x, connection.centroid.y, thickness=(weight * 20.0) + 1.0, stroke=place.color)
            dX = place.centroid.x - connection.centroid.x
            dY = place.centroid.y - connection.centroid.y
            length = math.sqrt(dX**2 + dY**2)
            if dX < 0:
                length *= -1.0
            try:    
                slope = -1.0 * (dX / dY)    # perpendicular line is slope flipped and negated
            except ZeroDivisionError:
                slope = float("inf")                    
            center = (place.centroid.x + connection.centroid.x) / 2.0, (place.centroid.y + connection.centroid.y) / 2.0                
            control = get_ctl(center[0], center[1], length * 0.25, slope)

            fill = 0.0472, 0.7792, place.color[0], 0.75
            # fill = 0., 0., 0., 0.75
            # thickness = (weight * 20.0) + 1.0   # for weighted
            thickness = science.scale(weight, 0.0, 1.0, 15.0, 60.0) # for nyc
            # thickness = 15.0   # for uniform, small
            fill = 0., 0., 0.
            ctx.curve(place.centroid.x, place.centroid.y, control[0], control[1], connection.centroid.x, connection.centroid.y, thickness=thickness, stroke=fill)

        # # draw paths
        # colors = [(0.0, 1.0, 1.0), (0.55, 1.0, 1.0), (0.33, 1.0, 1.0), (0.75, 1.0, 1.0)]        
        # for path in place.paths:
        #     if path.speed_index is None:
        #         continue
        #     for p, point in enumerate(path[:-1]):
        #         next = path[p+1]
        #         ctx.line(point.x, point.y, next.x, next.y, thickness=0.25, stroke=colors[path.speed_index]) # adjust thickness as necessary
        pass

    # # draw places
    # max_points = max([len(place.points) for place in places])
    # for place in places:
    #     weight = len(place.points) / float(max_points)        
    #     fill = 0.0472, 0.7792, place.color[0]
    #     ctx.arc(place.centroid.x, place.centroid.y, ((weight * 10.0) + 5.0)  / ctx.width, thickness=3.0, stroke=(0., 0., 1.0), fill=fill)

    # draw places, alt
    max_points = max([len(place.points) for place in places])
    for place in places:
        weight = len(place.points) / float(max_points)        
        fill = 0.0472, 0.7792, place.color[0]
        fill = 0., 0., 0.
        # size = science.scale(weight, 0.0, 1.0, 15.0, 30.0) - 3
        size = 8
        ctx.arc(place.centroid.x, place.centroid.y, size / ctx.width, thickness=0.0, stroke=(0., 0., 1.0), fill=fill)

    # draw alignment guides
    # ctx.rect(upper_left.x, upper_left.y, 10. / ctx.width, 10. / ctx.width, thickness=0., fill=(0.55, 1., 1.))
    # ctx.rect(lower_right.x, lower_right.y, 10. / ctx.width, 10. / ctx.width, thickness=0., fill=(0.55, 1., 1.))

    # ctx.show()
    ctx.image.save("screenshots/%s_geograph_%s,%s_.png" % (int(time.time()), city.centroid.lat, city.centroid.lon))
    # get_map(city, (upper_left, lower_right))


def normalize_points(points):
    min_x = min([point.x for point in points])
    min_y = min([point.y for point in points])
    for point in points:
        point.x -= min_x
        point.y -= min_y
    factor = max(max([point.x for point in points]), max([point.y for point in points]))
    for point in points:
        point.x /= factor
        point.y /= factor        


def get_map(city, bounds):

    CLOUDMADE_KEY = "9e44428bdd434d7697b10be5f975b849"
    STYLE_ID = 63595
    ZOOM = 12

    params = {  #'center': "%s,%s" % (city.centroid.lat, city.centroid.lon),
                #'zoom': ZOOM,    
                'bbox': "%s,%s,%s,%s" % (bounds[0].lat, bounds[0].lon, bounds[1].lat, bounds[1].lon),
                'size': "%sx%s" % (SIZE[0], SIZE[1]),
                'format': "png",
                'styleid': STYLE_ID,
                'marker': "size:big|url:%s|opacity:1.0|%s,%s|%s,%s" % ("http://brianhouse.net/download/quotidio_marker.png", bounds[0].lat, bounds[0].lon, bounds[1].lat, bounds[1].lon),
                }
    urlstring = "http://staticmaps.cloudmade.com/%s/staticmap" % CLOUDMADE_KEY
        
    print
    urlstring = "%s?%s" % (urlstring, net.urlencode(params))
    print urlstring
    
    try:    
        net.grab(urlstring, "screenshots/%s_geograph_%s,%s_map.png" % (int(time.time()), city.centroid.lat, city.centroid.lon))
    except Exception as e:
        log.error(log.exc(e))


