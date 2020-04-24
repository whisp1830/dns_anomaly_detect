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

def get_client_total(client_ip, table_name, cursor):
    sql = '''
        SELECT COUNT(query_id) 
        FROM %s
        WHERE query_client_ip='%s'
    '''%(table_name, client_ip)
    cursor.execute(sql)
    return cursor.fetchone()[0]

def get_suspect_client_ips(table_name, cursor):
    sql = '''
        SELECT DISTINCT query_client_ip 
        FROM %s
        WHERE query_fld IN
        (
            SELECT domain FROM domain_black_list
        )
    '''%table_name
    cursor.execute(sql)
    res = [ i[0] for i in cursor.fetchall()]
    return res

def get_client_preferences(client_ip, table_name, cursor):
    sql = '''
        SELECT query_fld, COUNT(query_id) as cnt
        FROM %s
        WHERE query_client_ip='%s' AND
        query_fld NOT IN 
        (
            SELECT domain FROM domain_white_list
        )
        GROUP BY query_fld
        ORDER BY cnt DESC
    '''%(table_name, client_ip)
    cursor.execute(sql)
    res = list(filter(lambda x:x[1]>5, cursor.fetchall()))
    return res

def get_client_dangerous(client_ip, table_name, cursor):
    sql = '''
        SELECT query_domain, query_time
        FROM %s
        WHERE query_client_ip='%s' AND
        query_fld IN
        (
            SELECT domain FROM domain_black_list
        )
    '''%(table_name, client_ip)
    cursor.execute(sql)
    res = cursor.fetchall()
    return {
        "dangerous_visits" : res,
        "total" : len(res)
    }

if __name__ == "__main__":
    traffic_date = "2020_01_07"
    table_name = "queries_" + traffic_date
    ips = get_suspect_client_ips(table_name, cursor)
    print ("共有%s个可疑client ip"%len(ips))

    for ip in ips:
        res = {}
        res["total"] = get_client_total(ip, table_name, cursor)
        res["client_ip"] = ip
        res["preferences"] = get_client_preferences(ip, table_name, cursor)
        res["dangerous"] = get_client_dangerous(ip, table_name, cursor)
        db.suspect_ip.insert_one(res)