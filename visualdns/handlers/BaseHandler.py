import pymysql
from pymongo import MongoClient
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, connectors):

        self.cursor = connectors.cursor
        self.db = connectors.db
        self.domain_white_list = connectors.domain_white_list
        self.white_note = connectors.white_note
        self.domain_black_list = connectors.domain_black_list
        self.black_note = connectors.black_note 
        self.city_locate = connectors.city_locate
        self.asn_locate = connectors.asn_locate



    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*") # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')