import pymongo
import pymysql

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['domain_frequency']
print ("MongoDB数据库连接成功")
connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()

sql = '''
    SELECT domain, note FROM domain_black_list
'''
cursor.execute(sql)
black_res = cursor.fetchall()

sql = '''
    SELECT domain, note FROM domain_white_list
'''
cursor.execute(sql)
white_res = cursor.fetchall()

for i in black_res:
    if db.domain_control.count_documents({'domain': i[0]}):
        db.domain_control.update_one(
            {"domain": i[0]},
            {
                "$set":{
                    "note" : i[1],
                    "type" : "危险域名"
                }
            }
        )
for i in white_res:
    if db.domain_control.count_documents({'domain': i[0]}):
        db.domain_control.update_one(
            {"domain": i[0]},
            {
                "$set":{
                    "note" : i[1],
                    "type" : "安全域名"
                }
            }
        )