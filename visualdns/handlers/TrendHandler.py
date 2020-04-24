import json
import math
import random
import pymysql
import datetime
import tornado.web
from dateutil import parser
from handlers.BaseHandler import BaseHandler

class TrendHandler(BaseHandler):
    def get(self,data):
        res = {}
        if "." in data:
            res = self.domainTrend(data)
        else:
            trend_date = parser.parse(data)
            res = self.trafficTrend(trend_date)
        
        self.write(json.dumps(res))

    def trafficTrend(self, trend_date):
        content = self.db.hourly_analysis.find({
                    "traffic_duration":{
                        "$gte": trend_date,
                        "$lt": trend_date+datetime.timedelta(days=1)
                    }
                },
                { "_id":0}
            ).sort("traffic_duration")
        res = {
            "dates" : [],
            "amounts" : []
        }
        for c in content:
            res["dates"].append(str(c["traffic_duration"]))
            res["amounts"].append(c["total_amount"])
        return res

    def domainTrend(self, domain):
        content = self.db.domain_control.find({
            "domain" : domain
        },
        {
            "_id" : 0
        })[0]

        res = {
            "dates" : [],
            "traffic": [],
            "visitors": [],
            "active_sub_domains": []
        }
        hourly_history = content["hourly_history"]
        base_traffic = max([ i["traffic"] for i in hourly_history])
        base_visitors = max([ i["visitors"] for i in hourly_history])
        base_active_sub_domains = max([ i["active_sub_domains"] for i in hourly_history])
        print (hourly_history)
        for c in hourly_history:
            prefix1 = random.randint(2,9)*random.randint(2,9)*random.randint(2,9)/1000
            prefix2 = random.randint(2,9)*random.randint(2,9)*random.randint(2,9)/1000
            prefix3 = random.randint(15,18)*random.randint(15,18)*random.randint(2,5)/2000
            res["dates"].append(str(c["traffic_duration"]))
            res["traffic"].append(c["traffic"]+prefix1*base_traffic)
            res["visitors"].append(math.floor(c["visitors"]+ prefix2*base_visitors))
            res["active_sub_domains"].append(math.floor(c["active_sub_domains"] + base_active_sub_domains*prefix3))
        print (res)
        return res