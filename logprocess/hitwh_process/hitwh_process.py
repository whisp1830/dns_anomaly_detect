import sys
import time
import kafka
import pymysql
from multiprocessing import Process
from domain_filters import *
from bloom_filter import BloomFilter
from dateutil import parser
from tld import get_fld


#producer = kafka.KafkaProducer(bootstrap_servers=['localhost:9092'])

connection = pymysql.connect(host='localhost',
                        port=3306,
                        user='root',
                        password='',
                        database='dns_flow')
cursor = connection.cursor()
print ("数据库连接成功")

visited_domain_filter = BloomFilter(
    max_elements=10000000, 
    error_rate=0.1, 
    filename="/Users/whisp/Mycode/dns_anomaly_detect/logprocess/hitwh_process/visited_domain.filter"
)
print ("已访问域名名单装载完毕")
safe_domain_filter = get_safe_domain_filter(
    max_elements=100000, 
    error_rate=0.1, 
    filename="/Users/whisp/Mycode/dns_anomaly_detect/logprocess/hitwh_process/safe_domain.filter",
    cursor=cursor
)
print ("白名单装载完毕")
black_domain_filter = get_black_domain_filter(cursor)
print ("黑名单装载完毕")


def feed_kafka_query(query_time, query_fld, query_domain, query_client_ip):
    sending = str(query_time.strftime('%s')) + "," + query_fld + "," + query_domain + "," + query_client_ip
    future = producer.send('queries', value= bytes(sending, encoding="utf-8"), partition= 0)
    print (sending)

def log_parser(single_log : str, last_info: tuple):
    '''
    将原始日志str解析为 query_info, reply_info 对象
    returnType: tuple, tuple, tuple
    '''
    single_log = single_log.replace(";", " ").split()
    query_time = parser.parse(single_log[2] + " " + single_log[3]).replace(microsecond=0) 
    query_client_ip = single_log[5]
    query_domain = single_log[9]

    if last_info[0] == query_time and last_info[1] == query_domain and last_info[2] == query_client_ip:
        return (), last_info
    if len(query_domain)>5 and query_domain[-5:] == ".arpa":
        return (), last_info
    
    last_info = (query_time, query_domain, query_client_ip)

    try:
        query_fld = get_fld(query_domain, fail_silently=True, fix_protocol=True)
        if not query_fld:
            query_fld = "INVALID"
        elif len(query_fld) > 45:
            return (), last_info 
    except:
        query_fld = "INVALID"

    return  (query_time, query_domain, query_fld, query_client_ip), \
            last_info

def create_new_table(date):
    sql = "DROP TABLE IF EXISTS `queries_%s`;"%date
    cursor.execute(sql)
    sql = '''
        CREATE TABLE `queries_%s` (
        `query_id` int NOT NULL AUTO_INCREMENT,
        `query_time` datetime NOT NULL,
        `query_domain` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
        `query_client_ip` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
        `query_fld` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
        PRIMARY KEY (`query_id`),
        KEY `by_time` (`query_time`) USING BTREE,
        KEY `by_domain` (`query_domain`) USING BTREE,
        KEY `by_fld` (`query_fld`) USING BTREE,
        KEY `by_client_ip` (`query_client_ip`) USING BTREE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
    '''%date
    cursor.execute(sql)

def query_info_sql(info):
    print ("正在写入数据库")
    date = str(info[0][0]).split()[0].replace("-", "_")
    query_table_name = "queries_" + date
    sql = "INSERT INTO "+ query_table_name + "(query_time, query_domain, query_fld, query_client_ip) VALUES(%s, %s, %s, %s)"
    cursor.executemany(sql, info)
    connection.commit()
    print ("+100000")

def get_distinct_fld(date, cursor):
    sql = "SELECT DISTINCT query_fld FROM queries_"+date+" WHERE query_fld NOT IN "\
        "(SELECT domain FROM domain_white_list)"
    cursor.execute(sql)
    res = cursor.fetchall()
    return res

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv)>1 else "log20.log"
    count = 0
    date = ""
    print (filename)
    with open(filename, "r") as f:
        single_log = f.readline()
        last_info = ("", "", "")
        info, last_info = log_parser(single_log, last_info)
        date = str(info[0]).split()[0].replace("-", "_")
        #create_new_table(date, cursor)
        query_infos = []
        long_query_infos = []
        black_query_infos = []
        print ("正在进行日志处理")
        while single_log:
            info, last_info = log_parser(single_log, last_info)
            if info:
                if len(info[1])>50:
                    long_query_infos.append(info)
                else:
                    if info[2] not in safe_domain_filter:
                        #feed_kafka_query(info[0], info[1], info[2], info[3])
                        if info[2] in black_domain_filter:
                            black_query_infos.append((info[3], date))
                    query_infos.append(info)
            single_log = f.readline()
            count += 1
            if count % 100000 == 0:
                p1 = Process(target=query_info_sql, args=(query_infos,))
                p1.start()
                print ("已处理日志", count)
                query_infos = []
                print ("正在进行日志处理")
                
    
    sql = "INSERT INTO long_domain_queries"\
        "(query_time, query_domain, query_fld, query_client_ip) VALUES(%s, %s, %s, %s)"
    cursor.executemany(sql, long_query_infos)
    sql = "INSERT INTO suspect_client_ip(ip, date, value) VALUES(%s, %s, 1) "\
        "ON DUPLICATE KEY UPDATE value=value+1"
    cursor.executemany(sql, black_query_infos)
    connection.commit()
    tobe_check = []
    for record in get_distinct_fld(date, cursor):
        domain = record[0]
        if domain not in visited_domain_filter:
            print (domain)
            sql = '''
                INSERT INTO domain_first_seen 
                SELECT query_fld, MIN(query_time)
                FROM queries_2020_01_07
                WHERE query_fld=%s
            '''
            cursor.execute(sql ,domain)
            visited_domain_filter.add(domain)
            tobe_check.append(domain)
    with open("拉清单.txt","a") as f:
        for i in tobe_check:
            f.write(i+"\n")
    connection.commit()
