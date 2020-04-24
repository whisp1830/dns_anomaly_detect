import datetime
import pymysql
import pymongo
import calendar
from dateutil import parser

connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['domain_frequency']

