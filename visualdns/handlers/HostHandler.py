import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(BASE_DIR)

import math
import json
import random
import datetime
from BaseHandler import BaseHandler

class HostHandler(BaseHandler):
    def get(self, data):
        res = {"ip":data}
        response = self.city_locate.city(data)
        res["country"] = response.country.name
        res["city"] = response.city.name
        res["network"] = response.traits.network
        res["latitude"], res["longitude"] = response.location.latitude, response.location.longitude
        r2 = self.asn_locate.asn(data)
        res["system_number"] = r2.autonomous_system_number
        res["system_organization"] = r2.autonomous_system_organization
        self.render("host_detail.html", info=res)
