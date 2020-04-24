import sys,os
import random
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径

sys.path.append(BASE_DIR)

from BaseHandler import BaseHandler

class PollutePageHandler(BaseHandler):
    def get(self):
        sql = '''
            select max(query_time) mqt,query_fld from queries where
            query_fld in (
                SELECT domain from domain_block_list
            ) GROUP BY query_fld
            UNION
            select max(query_time) mqt,query_fld from queries_2020_01_07 where
            query_fld in (
                SELECT domain from domain_block_list
            ) GROUP BY query_fld
            ORDER BY mqt DESC
        '''
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        sql = "SELECT domain, fake_ip FROM domain_block_list"
        self.cursor.execute(sql)
        raw = self.cursor.fetchall()
        domain_ip = {}
        for f in raw:
            domain_ip[f[0]] = f[1]
        res = [ [i[0], i[1], domain_ip[i[1]], self.asn_locate.asn(domain_ip[i[1]]).autonomous_system_organization] for i in res ]
        self.render("pollution.html", info=res)