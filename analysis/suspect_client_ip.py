import pymysql
import pymongo

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

def get_suspect_client_ips():
    sql = '''
        SELECT query_client_ip 
        FROM queries_2020_01_07
        WHERE query_fld IN
        (
            SELECT domain FROM domain_black_list
        )
    '''
    cursor.execute(sql)
    res = [ i[0] for i in cursor.fetchall()]
    return res

def get_client_preferences(client_ip):
    sql = '''
        SELECT COUNT(query_id) 
        FROM queries_2020_01_07
        WHERE query_client_ip=%s
    '''
    cursor.execute(sql, client_ip)
    total = cursor.fetchone()[0]

    sql = '''
        SELECT query_fld, COUNT(query_id) as cnt
        FROM queries_2020_01_07
        WHERE query_client_ip=%s AND
        query_fld NOT IN 
        (
            SELECT domain FROM domain_white_list
        )
        GROUP BY query_fld
        ORDER BY cnt DESC
    '''
    cursor.execute(sql, client_ip)
    res = list(filter(lambda x:x[1]>5, cursor.fetchall()))
    return {
        "client_ip" : client_ip,
        "prefers" : res,
        "total" : total
    }

def get_client_dangerous(client_ip):
    sql = '''

    '''

if __name__ == "__main__":
    ips = get_suspect_client_ips()
    for ip in ips:
        print (get_client_preferences(ip))