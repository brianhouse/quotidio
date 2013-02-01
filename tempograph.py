import json, sys, os, time, datetime, math, random
import numpy as np
from housepy import config, log, util, strings, science, drawing

SIZE = 1000.0

def draw(days):
    ctx = drawing.Context(int(SIZE), int(SIZE), hsv=True)
    center = SIZE / 2.0, SIZE / 2.0
    ring_width = (SIZE / 2.0) / (len(days) + 1)
    segment_degrees = 360.0 / 1440.0
    print("ring_width: %s" % ring_width)        
    print("segment_degrees: %s" % segment_degrees)        
    for ring, day in enumerate(days):
        for m, point in enumerate(day):
            if point is None:
                continue
            start = (m / 1440.0) * 360.0               
            end = start + segment_degrees 
            thickness = ring_width - (0.005 * SIZE)
            if not point.moving:
                color = point.place.color
            else:
                # color = (point.paths[0].start_place.color[0] + point.paths[0].end_place.color[0]) / 2.0, 1.0, 1.0
                color = point.paths[0].start_place.color
                thickness /= 2.0
            ctx.arc(*center, radius_x=(ring + 1) * ring_width, start=start - 90, end=end - 90, thickness=thickness, stroke=color)
            # ok, so instead, can we do the math and calculate the xy of the start, and connect lines? then we can use spiral?
    ctx.show()
    ctx.image.save("screenshots/%s_tempograph.png" % int(time.time()))
