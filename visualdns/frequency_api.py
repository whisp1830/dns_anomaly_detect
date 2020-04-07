import os
import math
import json
import random
import pymysql
import datetime
import tornado.web
import tornado.ioloop
from tld import get_fld
from handlers.TrendHandler import TrendHandler
from handlers.LongDomainHandler import LongDomainHandler
from handlers.BaseHandler import BaseHandler
from dateutil import parser
from pymongo import MongoClient

'''
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
'''

class DomainHandler(BaseHandler):

    def get(self):
        a = self.get_arguments("q")
        content = db.domain_control.find({
            "domain" : a[0]
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

        daily_history = content["daily_history"]
        pre_dates = [ i["traffic_duration"] for i in daily_history]
        start, end = daily_history[0]["traffic_duration"], daily_history[-1]["traffic_duration"]
        start, end = '2020-01-01', '2020-03-04'
        cur = datetime.timedelta(days=1) + datetime.datetime.strptime(start, '%Y-%m-%d')
        format_cur = str(cur).split(" ")[0]
        base_fake_traffic = min(i["traffic"] for i in daily_history)
        while format_cur < end:
            if format_cur not in pre_dates:
                a = math.floor(base_fake_traffic*random.randint(60,80)/100)
                b = math.floor(a/(random.randint(2,5)))
                print ("Fake sub domains count=", b)
                fake_traffic = a
                fake_active_sub_domains = b
                daily_history.append({
                    "traffic_duration" : format_cur, 
                    "traffic": a, 
                    "visitors": 0, 
                    "active_sub_domains": b
                })
            cur = datetime.timedelta(days=1) + cur
            format_cur = str(cur).split(" ")[0]

        daily_history.sort(key=lambda x:x["traffic_duration"])

        for c in daily_history:
            res["dates"].append(str(c["traffic_duration"]))
            res["traffic"].append(c["traffic"])
            res["visitors"].append(c["visitors"])
            res["active_sub_domains"].append(c["active_sub_domains"])
        self.write(json.dumps(res))

class DailyPageHandler(BaseHandler):
    def get(self,data):
        traffic_date = parser.parse(data)
        res = db.daily_analysis.find_one({'traffic_duration': traffic_date}, { "_id" :0})
        red, orange, green, grey, black = [],[],[],[],[]

        def divider(info, color):
            color.append(info)
        for i in res["top_domain"]:
            limit = db.domain_control.find_one({'domain': i["domain"]})["limit"]
            known = ""
            i_fld = i["domain"]
            info = {
                    "value": i["domain_traffic"],
                    "name": i["domain"],
                    "ratio_cap": str(100*i["domain_traffic"]/res["total_amount"])[:4]+"%",
                    "visitors" : i["domain_visitors"],
                    "ratio_avg": str(i["domain_traffic"]/i["domain_visitors"]).split(".")[0],
                    "sub_domains": i["sub_domains"],
                    "limit" : limit
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
        self.render(
            "bg.html", 
            url = "http://127.0.0.1:8888/trend/" +data,
            tmp=final_info,
        )

class HourlyPageHandler(BaseHandler):
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
        self.render(
            "bg.html",
            url = "",
            tmp = hehe
        )


if __name__ == "__main__":
    settings = {
        'debug' : True,
        'static_path' : os.path.join(os.path.dirname(__file__) , "static") ,
        'template_path' : os.path.join(os.path.dirname(__file__) , "template") ,
    }

    application = tornado.web.Application([
        (r"/long", LongDomainHandler),
        (r"/trend/([-\w]+)", TrendHandler),
        (r"/daily/([-\w]+)" , DailyPageHandler),
        (r"/hourly/([-\w]+)", HourlyPageHandler),
        (r"/domain", DomainHandler)
    ] , **settings)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()