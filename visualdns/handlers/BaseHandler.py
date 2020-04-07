import pymysql
from pymongo import MongoClient
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
        print ("MySQL数据库连接成功")
        self.cursor = connection.cursor()
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['domain_frequency']
        print ("MongoDB数据库连接成功")

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*") # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')