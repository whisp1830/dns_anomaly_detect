import tornado.web
import pymysql
from handlers.BaseHandler import BaseHandler

class LongDomainHandler(BaseHandler):
    
    def get(self):
        sql = "SELECT domain FROM domain_white_list"
        self.cursor.execute(sql)
        domain_white_list = set([i[0] for i in self.cursor.fetchall()])

        sql = '''
            SELECT query_time, query_domain, query_client_ip, query_fld
            FROM long_domain_queries
            ORDER BY query_id DESC LIMIT 100
        '''
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        res1, res2 = [], []
        for i in res:
            if i[3] not in domain_white_list:
                res1.append(i)
            else:
                res2.append(i)
        self.render("longdomain.html", unknown=res1, known=res2)