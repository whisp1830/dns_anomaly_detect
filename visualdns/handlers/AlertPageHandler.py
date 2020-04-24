import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(BASE_DIR)

import math
import json
import random
import datetime
from BaseHandler import BaseHandler

class AlertPageHandler(BaseHandler):
    def get(self):
        self.render("alert_detail.html")