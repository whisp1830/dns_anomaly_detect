from tld import get_fld
from dateutil import parser
from handlers.BaseHandler import BaseHandler

class HourlyPageHandler(BaseHandler):
    def get(self,data):
        traffic_date = parser.parse(data)
        res = self.db.hourly_analysis.find_one({'traffic_duration': traffic_date}, { "_id" :0})
        red, orange, green, grey, black = [],[],[],[],[]

        def divider(info, color):
            color.append(info)
        def worth(x):
            return x["value"] > 5
        for i in res["top_domain"]:
            i_fld = ""
            known = ""
            try:
                i_fld = get_fld(i["domain"], fail_silently=True, fix_protocol=True)
            except:
                i_fld = "INVALID"
            info = {
                    "value": i["domain_traffic"],
                    "name": i["domain"],
                    "ratio_cap": str(100*i["domain_traffic"]/res["total_amount"])[:4]+"%",
                    "visitors" : i["domain_visitors"],
                    "ratio_avg": str(i["domain_traffic"]/i["domain_visitors"]).split(".")[0],
            }
            if i_fld in self.domain_black_list and int(info["value"]) > 10:
                info["type"] = "有害域名"
                divider(info, red)
            elif i_fld in self.domain_white_list:
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
            else:
                black.append(i)
        del grey
        red.sort(key=lambda x: int(x["ratio_avg"]), reverse=True)
        orange.sort(key=lambda x: int(x["ratio_avg"]), reverse=True)
        others = list(filter(worth, black+green))
        others.sort(key=lambda x: int(x["value"]), reverse=True)
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
            "hourly_report_table.html", 
            url = "http://127.0.0.1:8888/trend/" + data[:-3],
            tmp=final_info,
        )
