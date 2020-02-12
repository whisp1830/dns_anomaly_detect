import pymysql
from dateutil import parser
from tld import get_fld

def log_parser(single_log : str):
    single_log = single_log.replace(";", " ").split()
    query_time = parser.parse(single_log[2] + " " + single_log[3])
    query_client_ip = single_log[5]
    client_type = single_log[8].strip(";") #客户端身份，教师或学生
    query_domain = single_log[9]
    try:
        query_fld = get_fld(query_domain, fail_silently=True, fix_protocol=True)
    except:
        query_fld = "INVALID"
    query_type = single_log[11]
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

def query_info_sql(info, cursor):
    cursor.execute('''
            INSERT INTO 
            `queries`(`query_time`, `query_domain`, `query_fld`, 
            `query_client_ip`, `client_type`)
            VALUES(%s, %s, %s, %s, %s)
            ''',(info['query_time'],
            info['query_domain'],
            info['query_fld'],
            info['query_client_ip'],
            info['client_type']))

def reply_info_sql(info, cursor):
    cursor.execute('''
            INSERT INTO 
            `replies`(`reply_time`, `reply_domain`,
            `reply_cnames`, `reply_as`, `reply_aaaas`)
            VALUES(%s, %s, %s, %s, %s)
            ''',(info['query_time'],
            info['query_domain'],
            ";".join(info['reply_cnames']),
            ";".join(info['reply_as']),
            ";".join(info['reply_aaaas'])))



if __name__ == "__main__":
    connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='',
                             db='dns_flow',
                             charset='utf8')
    print ("数据库连接成功")
    count = 0
    cursor = connection.cursor()
    with open("log20.log", "r") as f:
        single_log = f.readline()
        while count < 100000:
            info = log_parser(single_log)
            reply_info_sql(info, cursor)
            query_info_sql(info, cursor)
            count += 1
            single_log = f.readline()
            if count % 1000 == 0:
                connection.commit()
                print (count)
        connection.commit()