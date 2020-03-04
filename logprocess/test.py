import os
import pymysql

connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='',
                             db='dns_flow',
                             charset='utf8')
cursor = connection.cursor()
print ("MySQL数据库连接成功")

with open("top-10000.csv","r") as f:
    a = f.readlines()
    print (a)
sql = "INSERT INTO domain_white_list(domain) VALUES(%s)"
for i in a:
    try:
        i = i.strip().split(",")[1]
        cursor.execute(sql, i)
    except:
        print ("DUPLICATE KEY")
connection.commit()
connection.close()
print ("over")