#!/usr/bin/env python

import os
from housepy import database, util, net

CLOUDMADE_KEY = "9e44428bdd434d7697b10be5f975b849"
STYLE_ID = 63595
WIDTH = 640
HEIGHT = 480
ZOOM = 12

cities = [  (39.7119386606,-104.950620722),
            (40.7241002316,-73.9162034413),
            (41.7252473831,-74.0063800812),
            (44.9335235581,-93.219538549),
            (38.9482655525,-77.0590810776)
            ]


for city in cities:
        
    params = {  'center': "%s,%s" % (city[0], city[1]),
                'zoom': ZOOM,    
                'size': "%sx%s" % (WIDTH, HEIGHT),
                'format': "png",
                'styleid': STYLE_ID
                # 'marker': "size:big|url:%s|opacity:1.0|%s, %s" % ("http://brianhouse.net/download/marker.png", city[0], city[1]),
                }
    urlstring = "http://staticmaps.cloudmade.com/%s/staticmap" % CLOUDMADE_KEY
        
    urlstring = "%s?%s" % (urlstring, net.urlencode(params))
    print urlstring
        
    net.grab(urlstring, "screenshots/maps/map_%s,%s.png" % (city[0], city[1]))
    print "%s,%s" % (city[0], city[1])

