import pymysql
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()

sql = "SELECT query_time, query_domain FROM queries LIMIT 100000"
cursor.execute(sql)
res = cursor.fetchall()

for i in res:
    epoch_time = str(int(i[0].timestamp()))
    info = str(epoch_time+ " " +i[1]) 
    future = producer.send('queries' , 
                            value= bytes
                                (info,
                                encoding="utf-8"), 
                            partition= 0)
    result = future.get(timeout= 10)
    print(result)