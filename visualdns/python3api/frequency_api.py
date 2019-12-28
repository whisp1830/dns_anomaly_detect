import os
import json
import tornado.web
import tornado.ioloop
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['domain_frequency']
print ("MongoDB数据库连接成功")


class TrendHandler(tornado.web.RequestHandler):
    def get(self,date):
        content = db.hourly_analysis.find({},{ "_id":0})
        con = list(content)
        res = {
            "dates" : [],
            "amounts" : []
        }
        for c in con:
            res["dates"].append(c["traffic_duration"])
            res["amounts"].append(c["total_amount"])
        self.write(json.dumps(res))

class DailyHandler(tornado.web.RequestHandler):
    def get(self,data):
        res = db.daily_analysis.find_one({'traffic_duration': data}, { "_id" :0})
        tmp = []
        for i in res["top_domain"][:10]:
            tmp.append({
                "value": i["domain_traffic"],
                "name": i["domain"]
            })
        hehe = {
            "date" : data,
            "content" : tmp
        }
        tmp = json.dumps(hehe)
        self.write(tmp)


if __name__ == "__main__":
    settings = {
        'debug' : True,
        'static_path' : os.path.join(os.path.dirname(__file__) , "static") ,
        'template_path' : os.path.join(os.path.dirname(__file__) , "template") ,
    }

    application = tornado.web.Application([
        (r"/trend/([-\w]+)", TrendHandler),
        (r"/daily/([-\w]+)" , DailyHandler)       
    ] , **settings)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()