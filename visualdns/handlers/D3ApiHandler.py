import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径

sys.path.append(BASE_DIR)

import json
from BaseHandler import BaseHandler

class D3ApiHandler(BaseHandler):
    def get(self):
        raw,res = [],[]
        with open("flinkzayang", "rt") as f:
            raw = f.readlines()
        for r in raw:
            r = r.strip().split(",")
            name = r[2]
            value = r[3]
            date = r[1][:-2]
            res.append({
                "name" : name,
                "type" : name,
                "value" : value,
                "date" : date
            })

        self.write(json.dumps(res))