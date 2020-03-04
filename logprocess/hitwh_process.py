import time
import pymysql
from bloom_filter import BloomFilter
from dateutil import parser
from tld import get_fld

def log_parser(single_log : str, flag, last_info):
    single_log = single_log.replace(";", " ").split()
    query_time = parser.parse(single_log[2] + " " + single_log[3]).replace(microsecond=0) 
    query_client_ip = single_log[5]
    #client_type = single_log[8].strip(";") #客户端身份，教师或学生
    query_domain = single_log[9]
    if len(query_domain) > 90:
        query_domain = query_domain[-90:]
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
            query_fld = query_fld[-45:]
    except:
        query_fld = "INVALID"
    #query_type = single_log[11]
    '''
    reply_cnames, reply_as, reply_aaaas = [], [], []
    try:
        xmark = single_log.index("Response:")
        for i in range(xmark, len(single_log)):
            if single_log[i] == "CNAME":
                reply_cnames.append(single_log[i+1].strip(";"))
            elif single_log[i] == "A":
                reply_as.append(single_log[i+1].strip(";"))
            elif single_log[i] == "AAAA":
                reply_aaaas.append(single_log[i+1].strip(";"))
    except:
        pass
    '''
    if flag == "query":
        return (query_time, query_domain, query_fld, query_client_ip), last_info
    '''
    elif flag == "reply":
        return {
            "query_time" : query_time,
            "query_domain" : query_domain,           
            "reply_cnames" : reply_cnames,
            "reply_as" : reply_as,
            "reply_aaaas" : reply_aaaas
        }
    else:
        return {
            "query_time" : query_time,
            "query_type" : query_type,
            "query_domain" : query_domain, 
            "query_fld" : query_fld,
            "query_client_ip" : query_client_ip,
            "client_type" : client_type,            
            "reply_cnames" : reply_cnames,
            "reply_as" : reply_as,
            "reply_aaaas" : reply_aaaas
        }
    '''


def create_new_table(date, cursor):
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

def query_info_sql(info, cursor):
    print ("正在写入数据库")
    date = str(info[0][0]).split()[0].replace("-", "_")
    table_name = "queries_" + date
    sql = "INSERT INTO "+ table_name + "(query_time, query_domain, query_fld, query_client_ip) VALUES(%s, %s, %s, %s)"
    cursor.executemany(sql, info)

def reply_info_sql(info, cursor):
    try:
        cursor.execute('''
                INSERT INTO 
                "replies"("reply_time", "reply_domain",
                "reply_cnames", "reply_as", "reply_aaaas")
                VALUES(%s, %s, %s, %s, %s)
                ''',(info['query_time'],
                info['query_domain'],
                ";".join(info['reply_cnames']),
                ";".join(info['reply_as']),
                ";".join(info['reply_aaaas'])))
    except:
        pass

def get_distinct_fld(date, cursor):
    sql = "SELECT DISTINCT query_fld FROM queries_"+date+" WHERE query_fld NOT IN "\
        "(SELECT domain FROM domain_white_list)"
    cursor.execute(sql)
    res = cursor.fetchall()
    return res

if __name__ == "__main__":
    count = 0
    connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            database='dns_flow')
    print ("数据库连接成功")
    print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    domain_filter = BloomFilter(max_elements=10000000, error_rate=0.1, filename="test.test")
    count = 0
    date = ""
    cursor = connection.cursor()
    with open("log20.log", "r") as f:
        count = 0
        single_log = f.readline()
        last_info = ("", "", "")
        info,last_info = log_parser(single_log, "query", last_info)
        date = str(info[0]).split()[0].replace("-", "_")
        #create_new_table(date, cursor)
        query_infos = []
        while single_log:
            info,last_info = log_parser(single_log, "query", last_info)
            if info:
                query_infos.append(info)
            single_log = f.readline()
            count += 1
            if count % 100000 == 0:
                query_info_sql(query_infos, cursor)
                connection.commit()
                print (count)
                query_infos = []
        connection.commit()
    '''
    tobe_check = []
    for domain in get_distinct_fld(date, cursor):
        domain = domain[0]
        if domain not in domain_filter:
            print (domain)
            domain_filter.add(domain)
            tobe_check.append(domain)
    with open("拉清单.txt","a") as f:
        for i in tobe_check:
            f.write(i+"\n")
    '''
    print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                

    