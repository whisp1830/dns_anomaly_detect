import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(BASE_DIR)

import math
import json
import random
import datetime
from BaseHandler import BaseHandler

class FirstSeenHandler(BaseHandler):
    def get(self):
        self.cursor.execute(
            '''
                SELECT domain, first_seen_time
                FROM domain_first_seen
                ORDER BY first_seen_time DESC
                LIMIT 100
            '''
        )
        record = self.cursor.fetchall()
        self.render("firstseen.html", info=record)