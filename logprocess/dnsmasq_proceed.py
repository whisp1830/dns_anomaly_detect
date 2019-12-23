import pymysql
from kafka import KafkaProducer
from tld import get_fld
from dateutil import parser
'''
connection = pymysql.connect(host='106.15.250.172',
                             port=3306,
                             user='root',
                             password='069879ea8f',
                             db='dns_flow',
                             charset='utf8')
'''
'''
# 批量插入
effect_row = cursor.executemany(
    'INSERT INTO `users` (`name`, `age`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE age=VALUES(age)', [
        ('hello', 13),
        ('fake', 28),
    ])
    
connection.commit()
'''

#producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='',
                             db='dns_flow',
                             charset='utf8')
print ("数据库连接成功")
cursor = connection.cursor()

with open("dnsmasq.log","r") as f:
    query_list = []
    reply_list = []
    raw_records = f.readlines()
    for record in raw_records:
        if "query" in record:
            query_date = parser.parse(" ".join(record.split(" ")[:3]))
            query_domain = record.split(" ")[5]
            query_fld = get_fld(query_domain, fail_silently=True, fix_protocol=True)
            query_client_ip = record.split(" ")[-1]
            query_list.append((query_date, query_domain, query_fld, query_client_ip))
            '''
            future = producer.send('queries' , key= bytes(query_domain, encoding="utf-8"), 
                                    value= bytes(query_client_ip, encoding="utf-8"), partition= 0)
            '''
        elif "reply" in record:
            reply_date = parser.parse(" ".join(record.split(" ")[:3]))
            reply_domain = record.split(" ")[5]
            reply_answer = record.split(" ")[-1]
            reply_list.append((reply_date, reply_domain, reply_answer))
        elif "forwarded" in record:
            forwarded_date = parser.parse(" ".join(record.split(" ")[:3]))
            forwarded_domain = record.split(" ")[5]
            forwarded_ns_server = record.split(" ")[-1]
            try:
                cursor.execute('INSERT INTO `forwarded`(`forwarded_time`, `forwarded_domain`, `forwarded_ns_server`) VALUES(%s, %s, %s)',
                (forwarded_date, forwarded_domain, forwarded_ns_server))
            except:
                pass
        elif "cached" in record:
            cached_date = parser.parse(" ".join(record.split(" ")[:3]))
            cached_domain = record.split(" ")[5]
            cached_answer = record.split(" ")[-1]
            try:
                cursor.execute('INSERT INTO `cached`(`cached_time`, `cached_domain`, `cached_answer`) VALUES(%s, %s, %s)',
                (cached_date, cached_domain, cached_answer))
            except:
                pass
        else:
            print (record)
    connection.commit()


    cursor.executemany('INSERT INTO `queries`(`query_time`, `query_domain`, `query_fld`, `query_client_ip`) VALUES(%s, %s, %s, %s)', query_list)
    connection.commit()
    cursor.executemany('INSERT INTO `replies`(`reply_time`, `reply_domain`, `reply_answer`) VALUES(%s, %s, %s)', reply_list)
    connection.commit()

        