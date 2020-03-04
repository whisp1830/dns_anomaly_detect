import os
import json
import pymysql
import datetime
import tornado.web
import tornado.ioloop
from tld import get_fld
from dateutil import parser
from pymongo import MongoClient

connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()
client = MongoClient('mongodb://localhost:27017/')
db = client['domain_frequency']
print ("MongoDB数据库连接成功")

sql = "SELECT domain FROM domain_black_list"
cursor.execute(sql)
domain_black_list = set([i[0] for i in cursor.fetchall()])

sql = "SELECT domain FROM domain_white_list"
cursor.execute(sql)
domain_white_list = set([i[0] for i in cursor.fetchall()])


class DomainHandler(tornado.web.RequestHandler):
    def get(self):
        a = self.get_arguments("q")
        content = db.domain_control.find({
            "domain" : a[0]
        },
        {
            "_id" : 0
        })[0]
        self.write(json.dumps(content))

class TrendHandler(tornado.web.RequestHandler):
    def get(self,data):
        trend_date = parser.parse(data)
        content = db.hourly_analysis.find({
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

class DailyPageHandler(tornado.web.RequestHandler):
    def get(self,data):
        traffic_date = parser.parse(data)
        res = db.daily_analysis.find_one({'traffic_duration': traffic_date}, { "_id" :0})
        red, orange, green, grey, black = [],[],[],[],[]

        def divider(info, color):
            color.append(info)
        for i in res["top_domain"]:
            known = ""
            i_fld = i["domain"]
            info = {
                    "value": i["domain_traffic"],
                    "name": i["domain"],
                    "ratio_cap": str(100*i["domain_traffic"]/res["total_amount"])[:4]+"%",
                    "visitors" : i["domain_visitors"],
                    "ratio_avg": str(i["domain_traffic"]/i["domain_visitors"]).split(".")[0],
                    "sub_domains": i["sub_domains"],
                    "type" : ""
            }
            if i_fld in domain_black_list and int(info["value"]) > 10:
                info["type"] = "有害域名"
                divider(info, red)
            elif i_fld in domain_white_list:
                info["type"] = "知名域名"
                divider(info, green)
            else:
                info["type"] = "其他域名"
                divider(info, grey)
        threshold = max([ int(i["ratio_avg"]) for i in green])*0.75
        print ("threshold is ", threshold)
        for i in grey:
            if int(i["ratio_avg"]) > threshold :
                i["type"] = "可疑域名"
                orange.append(i)
            elif int(i["sub_domains"]) > 100:
                i["type"] = "可疑域名"
                orange.append(i)
            else:
                black.append(i)
        del grey
        red.sort(key=lambda x: int(x["ratio_avg"]), reverse=True)
        orange.sort(key=lambda x: int(x["ratio_avg"]), reverse=True)
        others = black+green
        others.sort(key=lambda x: int(x["value"]), reverse=True)
        final_info = {
            "date" : data,
            "total" : res["total_amount"],
            "content" : red + orange + others
        }
        url = "http://127.0.0.1:8888/trend/"+str(traffic_date).split()[0]
        self.render("bg.html", tmp=final_info, url= url)

class HourlyPageHandler(tornado.web.RequestHandler):
    def get(self,data):
        traffic_date = parser.parse(data)
        print (traffic_date)
        res = db.hourly_analysis.find_one({'traffic_duration': traffic_date}, { "_id" :0})
        print (res)
        tmp = []
        for i in res["top_domain"]:
            known = ""
            i_fld = i["domain"]
            if i_fld in domain_black_list:
                known = "有害域名"
            elif i_fld in domain_white_list:
                known = "知名域名"
            else:
                known = "其他"
            tmp.append({
                "value": i["domain_traffic"],
                "name": i["domain"],
                "ratio_cap": str(100*i["domain_traffic"]/res["total_amount"])[:4]+"%",
                "visitors" : i["domain_visitors"],
                "ratio_avg": str(i["domain_traffic"]/i["domain_visitors"]).split(".")[0],
                "type" : known
            })
        hehe = {
            "date" : data,
            "total" : res["total_amount"],
            "content" : tmp
        }
        self.render("bg.html", tmp=hehe)


if __name__ == "__main__":
    settings = {
        'debug' : True,
        'static_path' : os.path.join(os.path.dirname(__file__) , "static") ,
        'template_path' : os.path.join(os.path.dirname(__file__) , "template") ,
    }

    application = tornado.web.Application([
        (r"/trend/([-\w]+)", TrendHandler),
        (r"/daily/([-\w]+)" , DailyPageHandler),
        (r"/hourly/([-\w]+)", HourlyPageHandler),
        (r"/domain", DomainHandler)
    ] , **settings)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()