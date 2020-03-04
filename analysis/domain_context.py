import datetime
import pymysql
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

def getContext(domain, client_ip):
    sql = "SELECT query_domain "\
        "FROM queries_copy1 WHERE query_client_ip='%s' "%client_ip
    cursor.execute(sql)
    raw_history = cursor.fetchall()
    print (raw_history)
    client_ip_history = [""]
    for i in raw_history:
        i = i[0]
        if i != client_ip_history[-1]:
            client_ip_history.append(i)
    for i in client_ip_history:
        print (i)

getContext("ydy.com", "10.246.59.150")