import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径

sys.path.append(BASE_DIR)

import math
import json
import random
import datetime
from BaseHandler import BaseHandler

class ClientHandler(BaseHandler):
    def get(self, data):
        res = self.db.suspect_ip.find_one({'client_ip':data},{"_id":0})
        if not res:
            self.write("No data")
        else:
            self.render("client_detail.html", info=res)