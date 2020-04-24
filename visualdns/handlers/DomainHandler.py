import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径

sys.path.append(BASE_DIR)

import math
import json
import random
import datetime
from BaseHandler import BaseHandler

class DomainHandler(BaseHandler):
    def get(self, data):
        context = []
        known = "unknown"
        first_seen = "已认证的安全域名，不记录首次出现时间"
        if data in self.domain_white_list:
            known = "safe"
        elif data in self.domain_black_list:
            known = "dangerous"

        if known != "safe":
            self.cursor.execute(
                '''
                    SELECT first_seen_time
                    FROM domain_first_seen
                    WHERE domain=%s
                ''',
                data
            )
            first_seen = self.cursor.fetchone()[0]

        content = self.db.domain_control.find_one({
            "domain" : data
        },
        {
            "_id" : 0
        })

        domain_context = self.db.domain_context.find_one({
            "domain" : data
        },
        {
            "_id" : 0
        })
        if domain_context and  "context" in domain_context:
            context = domain_context["context"]
        
        tmp = content["ips"] if "ips" in content.keys() else []
        tmp.sort()
        res = {
            "name" : data,
            "sub_domains" : content["sub_domains"],
            "traffic_limit" : "UNLIMIT" if content["traffic_limit"]==10 or ("type" in content and content["type"]=="安全域名") else content["traffic_limit"]*3,
            "subdomain_limit" : content["subdomain_limit"] * 3,
            "visitor_limit" : max(50, content["visitor_limit"]*5),
            "first_seen_time" : str(first_seen),
            "ips" : tmp,
            "type" : content["type"] if "type" in content else "未知域名",
            "note" : content["note"] if "note" in content else "未知",
            "context" : context
        }
        url = "http://127.0.0.1:8888/trend/" + data
        self.render("domain_detail.html", info=res, url=url)