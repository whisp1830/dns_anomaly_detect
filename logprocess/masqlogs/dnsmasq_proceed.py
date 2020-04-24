import os
import pymysql
from kafka import KafkaProducer
from tld import get_fld
from dateutil import parser

#producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='',
                             db='dns_flow',
                             charset='utf8')
print ("数据库连接成功")
cursor = connection.cursor()

cursor.execute("SELECT MAX(query_time) FROM queries ")
last_date = cursor.fetchone()[0]

with open("dnsmasq.log","r") as f:
    query_list = []
    last_query_date, last_query_domain = "",""
    raw_records = f.readlines()
    for record in raw_records:
        if "query" in record:
            query_date = parser.parse(" ".join(record.split()[:3]))
            if last_date and query_date <= last_date:
                continue
            print (query_date)
            query_domain = record.split()[5]
            if len(query_domain)>5 and query_domain[-5:] == ".arpa":
                continue
            if last_query_date == query_date and last_query_domain == query_domain:
                continue
            query_fld = get_fld(query_domain, fail_silently=True, fix_protocol=True)
            if not query_fld:
                query_fld = "INVALID"
            query_client_ip = record.split()[-1]
            query_list.append((query_date, query_domain, query_fld, query_client_ip))
            last_query_date, last_query_domain = query_date, query_domain
            '''
            future = producer.send('queries' , key= bytes(query_domain, encoding="utf-8"), 
                                    value= bytes(query_client_ip, encoding="utf-8"), partition= 0)
            '''

    cursor.executemany("INSERT INTO `queries`(query_time, query_domain, query_fld, query_client_ip) VALUES(%s, %s, %s, %s)", query_list)
    connection.commit()

        