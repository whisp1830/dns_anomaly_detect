import os
import json
import pymysql
import tornado.web
import tornado.ioloop
from tld import get_fld
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

class TrendHandler(tornado.web.RequestHandler):
    def get(self,data):
        content = db.hourly_analysis.find({"time":{"$gte":datetime(2016,9,26),"$lt":datetime(2016,9,27)}},{ "_id":0})
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
                "ratio": str(100*i["domain_traffic"]/res["total_amount"])[:4]+"%",
                "type": known
            })
        hehe = {
            "date" : data,
            "total" : res["total_amount"],
            "content" : tmp
        }
        self.render("bg.html", tmp=hehe)

class HourlyHandler(tornado.web.RequestHandler):
    def get(self,data):
        data = data[:10] + " " + data[-2:]
        res = db.hourly_analysis.find_one({'traffic_duration': data}, { "_id" :0})
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
                "ratio": str(100*i["domain_traffic"]/res["total_amount"])[:4]+"%",
                "type": known
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
        (r"/daily/([-\w]+)" , DailyHandler),
        (r"/hourly/([-\w]+)", HourlyHandler),
        (r"/dnsflow", TrendPageHandler)       
    ] , **settings)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()