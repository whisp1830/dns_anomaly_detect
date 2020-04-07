import json
import pymysql
import datetime
import tornado.web
from dateutil import parser
from handlers.BaseHandler import BaseHandler

class TrendHandler(BaseHandler):
    def get(self,data):
        trend_date = parser.parse(data)
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
        
        self.write(json.dumps(res))