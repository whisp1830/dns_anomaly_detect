import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径

sys.path.append(BASE_DIR)

import json
from BaseHandler import BaseHandler

class D3PageHandler(BaseHandler):
    def get(self):
        self.render("d3page.html")