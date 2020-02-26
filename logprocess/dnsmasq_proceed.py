import os
import pymysql
import psycopg2
from kafka import KafkaProducer
from tld import get_fld
from dateutil import parser

#producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
'''
connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='',
                             db='dns_flow',
                             charset='utf8')
'''
connection = psycopg2.connect(host='pgm-bp1u51siu56415z7oo.pg.rds.aliyuncs.com',
                             port=1433,
                             user='whisp',
                             password='@Cty0807al',
                             database='dns_flow')
print ("数据库连接成功")
cursor = connection.cursor()
query_flag = input("将查询信息写入数据库吗")
reply_flag = input("将查询结果写入数据库吗")
cache_flag = input("将查询缓存写入数据库吗")

#os.system(" wget http://idpsys.xyz:88/dnsmasq.log")

with open("dnsmasq.log","r") as f:
    query_list = []
    reply_list = []
    last_query_date, last_query_domain = "",""
    raw_records = f.readlines()
    for record in raw_records:
        if "query" in record:
            query_date = parser.parse(" ".join(record.split()[:3]))
            query_domain = record.split()[5]
            if len(query_domain)>5 and query_domain[-5:] == ".arpa":
                continue
            if last_query_date == query_date and last_query_domain == query_domain:
                continue
            query_fld = get_fld(query_domain, fail_silently=True, fix_protocol=True)
            query_client_ip = record.split()[-1]
            query_list.append((query_date, query_domain, query_fld, query_client_ip))
            last_query_date, last_query_domain = query_date, query_domain
            '''
            future = producer.send('queries' , key= bytes(query_domain, encoding="utf-8"), 
                                    value= bytes(query_client_ip, encoding="utf-8"), partition= 0)
            '''
        '''
        elif "reply" in record:
            reply_date = parser.parse(" ".join(record.split()[:3]))
            reply_domain = record.split()[5]
            reply_answer = record.split()[-1]
            reply_list.append((reply_date, reply_domain, reply_answer))
            print (reply_date, reply_domain, reply_answer)
        elif "cached" in record:
            cached_date = parser.parse(" ".join(record.split()[:3]))
            cached_domain = record.split()[5]
            cached_answer = record.split()[-1]
            try:
                cursor.execute('INSERT INTO `cached`(`cached_time`, `cached_domain`, `cached_answer`) VALUES(%s, %s, %s)',
                (cached_date, cached_domain, cached_answer))
            except:
                pass
        '''

    cursor.executemany('INSERT INTO "queries"("query_time", "query_domain", "query_fld", "query_client_ip") VALUES(%s, %s, %s, %s)', query_list)
    connection.commit()
    cursor.executemany('INSERT INTO `replies`(`reply_time`, `reply_domain`, `reply_answer`) VALUES(%s, %s, %s)', reply_list)
    connection.commit()

        