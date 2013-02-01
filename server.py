#!/usr/bin/env python

import os, base64, time, tornado, json
from housepy import tornado_server, strings, log, util
from housepy.tornado_server import Handler
from almanac import Almanac

def main():
    handlers = [    
        (r"/?([^/]*)", Home),
    ]
    tornado_server.start(handlers)


class Home(Handler):

    def get(self, user_id):
        log.info("Home.get")

        if not len(user_id):
            return self.text("/user_id")
        user = self.db.get("SELECT * FROM users WHERE id=%s", user_id)
        if user is None:
            return self.text("User not found") 
            
        if not self.get_argument('partial', None):
            return self.render("page.html", user=user)

        log.info("--> generating partial")    

        almanac = Almanac.build(self.db, user_id)        # should be pulled from a cache
        
        if not almanac.current_point.moving:
            total_weight = sum([weight for place, weight in almanac.current_point.place.connections.items()])       # this goes in almanac somewhere
            weights = []
            for place, weight in almanac.current_point.place.connections.items():
                weights.append("%s (%f)" % (place.id, (weight / total_weight)))

        place = almanac.current_point.place if almanac.current_point.place is not None else None

        return self.render("content.html", place=place, weights=weights, user=user)


    def post(self, nop=None):        
        log.info("Home.post")
        user_id = self.get_argument('user_id', None)
        label = self.get_argument('label', None)
        if user_id is None or label is None:
            return self.error("Missing parameters")
        
        # what needs to happen here?
        # I need to pull the user's current place and label it
        # and / or, I need to create a label associated with a latlng
        # obviously, some future handling of duplicate labels, etc
        # actually, would be interesting if labels were temporally situated also, valid at a particular location until that location changes
        # time zone is a bitch, here. CE stores in datetimes, but OP is in timestamps, which is smart. so evenually labels should be timestamps; for now we're assuming constant timezone.
        # for now, we're going to symbiote on the ce database (assuming this is just really CE 2.0)

        self.db.execute("INSERT INTO labels (user_id, label) VALUES (%s, %s)", user_id, label)

        # so now the graph building has to take into account these labels and assign them to places.
        # could do this on the almanac level. sick.

        url = "/%s" % user_id
        return self.redirect(url)
        

if __name__ == "__main__":
    main()
    
    
