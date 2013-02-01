import json, sys, os, time, datetime, math, random
import numpy as np
from housepy import config, log, util, strings, science, drawing

SIZE = 1000.0
GAP = 5.0

def draw(week, brightness=1.0):
    background = 0., 0., 0.
    ctx = drawing.Context(int(SIZE), int(SIZE), hsv=True, background=background)
    day_width = (ctx.width + GAP) / 7.0
    minute_height = ctx.height / 1440.0
    for d, day in enumerate(week):
        for m, place in enumerate(day):
            if place is not None and place != -1:
                color = place.color
                color = color[0], color[1], brightness
            else:
                color = background
            ctx.rect(d * day_width, m * minute_height, day_width - GAP, minute_height - (GAP/2), thickness=0.0, fill=color)
    ctx.show()
    # ctx.image.save("screenshots/%s_calegraph.png" % int(time.time()))
