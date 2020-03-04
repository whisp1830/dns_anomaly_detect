import datetime
import pymysql
import pymongo
import calendar
from dateutil import parser

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



def get_latest_hour():
    latest_hour = {}
    try:
        latest_hour = db.hourly_analysis.find({}, {'_id':0, 'traffic_duration':1}).sort("traffic_duration",-1).limit(1)[0]
    except:
        latest_hour['traffic_duration'] = '1970-01-01 00'
    return latest_hour['traffic_duration']

def get_latest_date():
    latest_date = {}
    try:
        latest_date = db.daily_analysis.find({}, {'_id':0, 'traffic_duration':1}).sort("traffic_duration",-1).limit(1)[0]
    except:
        latest_date['traffic_duration'] = '1970-01-01'
    return str(latest_date['traffic_duration'])

def malicous_traffic_domain(start, end, duration_flag):
    if duration_flag == "fld":
        sql = '''
            SELECT query_fld,COUNT(query_id),COUNT(DISTINCT(query_client_ip)),COUNT(DISTINCT(query_domain)) 
            FROM queries_2020_01_07 
            WHERE query_fld IN 
            (SELECT domain FROM domain_black_list) 
            AND query_time BETWEEN '%s' AND '%s' 
            GROUP BY query_fld
            ORDER BY count(query_id) DESC 
        '''%(start, end)
    elif duration_flag == "domain":
        sql = '''
            SELECT query_domain,COUNT(query_id),COUNT(DISTINCT(query_client_ip)) 
            FROM queries_2020_01_07
            WHERE query_fld IN
            (SELECT domain FROM domain_black_list)
            AND query_time BETWEEN '%s' AND '%s'
            GROUP BY query_domain
            ORDER BY count(query_id) DESC            
        '''%(start, end)
    cursor.execute(sql)
    res = cursor.fetchall()
    return res


def top_traffic_domain_hour(query_date):
    start, end = str(query_date)+":00:00", str(datetime.timedelta(hours=1)+datetime.datetime.strptime(query_date, '%Y-%m-%d %H'))

    #用于生成每小时的域名访问综合报告 hourly_analysis
    hourly_malicious_domain_data = malicous_traffic_domain(start, end, "domain")
    sql =  "SELECT query_domain,COUNT(query_id),COUNT(DISTINCT(query_client_ip)) FROM queries_2020_01_07 "\
        "WHERE query_time BETWEEN '%s' AND '%s'"\
        "GROUP BY query_domain ORDER BY count(query_id) DESC LIMIT 200;"%(start, end)
    cursor.execute(sql)
    hourly_domain_data = cursor.fetchall()
    hourly_domain_data = list(set(hourly_domain_data).union(set(hourly_malicious_domain_data)))

    #用于生成每个域名的访问综合报告 domain_control
    hourly_malicious_domain_data2 = malicous_traffic_domain(start, end, "fld")
    sql =  "SELECT query_fld,COUNT(query_id),COUNT(DISTINCT(query_client_ip)),COUNT(DISTINCT(query_domain)) "\
        "FROM queries_2020_01_07 "\
        "WHERE query_time BETWEEN '%s' AND '%s' "\
        "GROUP BY query_fld ORDER BY count(query_id) DESC LIMIT 500;"% (start, end)
    cursor.execute(sql)
    hourly_domain_data2 = cursor.fetchall()
    hourly_domain_data2 = list(set(hourly_domain_data2).union(set(hourly_malicious_domain_data2)))
    record_domain_control(query_date, hourly_domain_data2, "hourly")
    print ("域名数据查询完成")

    sql =  "SELECT query_client_ip,COUNT(query_id),COUNT(DISTINCT(query_domain)) FROM queries_2020_01_07 "\
        "WHERE query_time BETWEEN '%s' AND '%s'"\
        "GROUP BY query_client_ip ORDER BY count(query_id) DESC LIMIT 200;"% (start, end)
    cursor.execute(sql)
    hourly_client_ip_data = cursor.fetchall()   
    print ("ClientIP 数据查询完成")

    sql = "SELECT COUNT(query_id) FROM queries_2020_01_07 "\
        "WHERE query_time BETWEEN '%s' AND '%s'"% (start, end)
    cursor.execute(sql)
    total_amount = cursor.fetchone()[0]

    sql = "SELECT COUNT(DISTINCT(query_domain)) FROM queries_2020_01_07 "\
        "WHERE query_time BETWEEN '%s' AND '%s'"% (start, end)
    cursor.execute(sql)
    count_distinct_domains = cursor.fetchone()[0]
    return {
        "traffic_duration": parser.parse(query_date), 
        "total_amount": total_amount,
        "distinct_domains": count_distinct_domains,
        "top_domain": [
            {"domain":i[0], "domain_traffic":i[1],  "domain_visitors": i[2]} for i in list(hourly_domain_data)
        ],
        "top_client_ip": [
            {"client_ip":i[0], "client_ip_traffic":i[1], "visit_domains": i[2]} for i in list(hourly_client_ip_data)
        ]
    }


def top_traffic_domain_day(query_date):
    print (query_date)
    start, end = query_date, str(datetime.timedelta(days=1)+datetime.datetime.strptime(query_date, '%Y-%m-%d')).split()[0]
    daily_malicious_domain_data = malicous_traffic_domain(start, end, "fld")
    sql = '''
        SELECT query_fld,COUNT(query_id),COUNT(DISTINCT(query_client_ip)),COUNT(DISTINCT(query_domain)) 
        FROM queries_2020_01_07 
        GROUP BY query_fld 
        ORDER BY count(query_id) DESC LIMIT 500;
    '''
    cursor.execute(sql)
    daily_domain_data = cursor.fetchall()
    daily_domain_data = list(set(daily_malicious_domain_data).union(set(daily_domain_data)))
    record_domain_control(query_date, daily_domain_data, "daily")
    print ("域名数据查询完成")

    sql =  "SELECT query_client_ip,COUNT(query_id),COUNT(DISTINCT(query_domain)) FROM queries_2020_01_07 "\
        "GROUP BY query_client_ip ORDER BY count(query_id) DESC LIMIT 500;"
    cursor.execute(sql)
    daily_client_ip_data = cursor.fetchall()
    print ("ClientIP 数据查询完成")

    sql = "SELECT COUNT(query_id) FROM queries_2020_01_07 "
    cursor.execute(sql)
    total_amount = cursor.fetchone()[0]

    sql = "SELECT COUNT(DISTINCT(query_domain)) FROM queries_2020_01_07 "
    cursor.execute(sql)
    count_distinct_domains = cursor.fetchone()[0]

    return {
        "traffic_duration": parser.parse(query_date), 
        "total_amount": total_amount,
        "distinct_domains": count_distinct_domains,
        "top_domain": [ 
            {"domain":i[0], "domain_traffic":i[1], "domain_visitors": i[2], "sub_domains": i[3]} for i in list(daily_domain_data)
        ],
        "top_client_ip": [
            {"client_ip":i[0], "client_ip_traffic":i[1], "visit_domains":i[2]} for i in list(daily_client_ip_data)
        ]
    }

def record_domain_control(query_date, infos, duration_flag):
    for info in infos:
        domain, traffic, visitors, active_sub_domains = info[0], info[1], info[2], info[3]
        has_previous_record = db.domain_control.count_documents({'domain': domain})
        sql = "SELECT DISTINCT query_domain FROM queries_2020_01_07 WHERE query_fld=%s"
        cursor.execute(sql, domain)
        sub_domains = set([ i[0] for i in cursor.fetchall()])
        print (duration_flag)
        if not has_previous_record:
            daily_history, hourly_history = [], []
            if duration_flag == "daily":
                daily_history = [{
                    "traffic_duration": query_date, 
                    "traffic": traffic,
                    "visitors": visitors,
                    "active_sub_domains": active_sub_domains
                }]
            elif duration_flag == "hourly":
                hourly_history = [{
                    "traffic_duration": query_date, 
                    "traffic": traffic,
                    "visitors": visitors,
                    "active_sub_domains": active_sub_domains
                }]
            res = {
                "domain" : domain,
                "sub_domains" : list(sub_domains),
                "limit" : 1,
                "daily_history": daily_history,
                "hourly_history": hourly_history,
            }
            db.domain_control.insert_one(res)
        else:
            pre = db.domain_control.find({"domain":domain},{'_id':0})[0]
            sub_domains = sub_domains.union(set(pre["sub_domains"]))
            if duration_flag == "daily":
                cur = pre["daily_history"] + [{
                    "traffic_duration": query_date, 
                    "traffic": traffic,
                    "visitors": visitors,
                    "active_sub_domains": active_sub_domains}]
                db.domain_control.update_one({"domain":domain}, 
                                            {"$set":{
                                                "sub_domains" : list(sub_domains),
                                                "daily_history" : cur
                                            }})
            elif duration_flag == "hourly":
                cur = pre["hourly_history"] + [{
                    "traffic_duration": query_date, 
                    "traffic": traffic,
                    "visitors": visitors,
                    "active_sub_domains": active_sub_domains}]
                db.domain_control.update_one({"domain":domain}, 
                                            {"$set":{
                                                "sub_domains" : list(sub_domains),
                                                "hourly_history" : cur
                                            }})  

def insert_hourly_data_into_mongodb(cursor):
    sql = "SELECT DISTINCT DATE_FORMAT(query_time, '%%Y-%%m-%%d %%H') FROM queries_2020_01_07 WHERE query_time >'%s'"%str(datetime.timedelta(hours=1)+datetime.datetime.strptime(get_latest_hour(), '%Y-%m-%d %H'))
    cursor.execute(sql)
    query_dates = cursor.fetchall()
    res = []
    for query_date in query_dates:
        res.append(top_traffic_domain_hour(query_date[0]))
    if res:
        db.hourly_analysis.insert_many(res)

def insert_daily_data_into_mongodb(cursor):
    sql = "SELECT DISTINCT DATE_FORMAT(query_time, '%%Y-%%m-%%d') FROM queries_2020_01_07 WHERE query_time> '%s'"%str(datetime.timedelta(days=1)+datetime.datetime.strptime(get_latest_date(), '%Y-%m-%d'))
    cursor.execute(sql)
    query_dates = cursor.fetchall()
    res = []
    for query_date in query_dates:
        res.append(top_traffic_domain_day(query_date[0]))
    if res:
        pass
        db.daily_analysis.insert_many(res)

     

def record_malicious_domains():
    sql = "SELECT domain FROM domain_black_list"
    cursor.execute(sql)
    malicious_domains = cursor.fetchall()
    for domain in malicious_domains:
        domain = domain[0]
        

    

if __name__ == "__main__":
    insert_daily_data_into_mongodb(cursor)
    insert_hourly_data_into_mongodb(cursor)
