import sys,os
import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径

sys.path.append(BASE_DIR)

from dateutil import parser
from BaseHandler import BaseHandler

class DailyPageHandler(BaseHandler):
    def get(self,data):
        traffic_date = parser.parse(data)
        pre_date, next_date = datetime.timedelta(days=-1)+traffic_date, datetime.timedelta(days=1)+traffic_date
        res = self.db.daily_analysis.find_one({'traffic_duration': traffic_date}, { "_id" :0})
        red, orange, green, grey, black = [],[],[],[],[]

        def divider(info, color):
            color.append(info)
        def worth(x):
            return True
        
        for i in res["top_domain"]:
            tmp = self.db.domain_control.find_one({'domain':i['domain']})
            note = tmp["note"] if "note" in tmp else ""
            domain_type = tmp["type"] if "type" in tmp else ""
            info = {
                    "value": i["domain_traffic"],
                    "name": i["domain"],
                    "ratio_cap": str(100*i["domain_traffic"]/res["total_amount"])[:4]+"%",
                    "visitors" : i["domain_visitors"],
                    "ratio_avg": str(i["domain_traffic"]/i["domain_visitors"]).split(".")[0],
                    "sub_domains": i["sub_domains"],
                    "note": note,
                    "type" : domain_type
            }
            if domain_type == "危险域名" and int(info["value"]) > 10:          
                divider(info, red)
            elif domain_type == "安全域名":
                divider(info, green)
            else:
                info["type"] = "未知域名"
                divider(info, grey)
        threshold = max([ int(i["ratio_avg"]) for i in green])*0.75
        for i in grey:
            if int(i["ratio_avg"]) > threshold :
                i["type"] = "可疑域名"
                i["note"] = "访问量过大"
                orange.append(i)
            elif int(i["sub_domains"]) > 50:
                i["type"] = "可疑域名"
                i["note"] = "活跃子域名过多"
                orange.append(i)
            else:
                black.append(i)
        del grey
        #red.sort(key=lambda x: int(x["ratio_avg"]), reverse=True)
        #orange.sort(key=lambda x: int(x["ratio_avg"]), reverse=True)
        others = list(filter(worth, black+green))
        #others.sort(key=lambda x: int(x["value"]), reverse=True)
        final_info = {
            "date" : data,
            "total" : res["total_amount"],
            "red_total" : sum([i["value"] for i in red]),
            "orange_total" : sum([i["value"] for i in orange]),
            "green_total" : sum([i["value"] for i in green]),
            "black_total" : sum([i["value"] for i in black]),
            "content" : red + orange + others
        }
        self.render(
            "daily_report_table.html", 
            pre_date = pre_date,
            next_date = next_date,
            url = "http://127.0.0.1:8888/trend/" +data,
            tmp=final_info,
            client = res["top_client_ip"]
        )