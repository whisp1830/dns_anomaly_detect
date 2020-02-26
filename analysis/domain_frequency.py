import datetime
import pymysql
import pymongo
import calendar

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
        latest_hour['traffic_duration'] = '1970-01-01 00:00:00'
    return latest_hour['traffic_duration']

def get_latest_date():
    latest_date = {}
    try:
        latest_date = db.daily_analysis.find({}, {'_id':0, 'traffic_duration':1}).sort("traffic_duration",-1).limit(1)[0]
    except:
        latest_date['traffic_duration'] = '1970-01-01'
    return latest_date['traffic_duration']


def top_traffic_domain_hour(query_date):
    sql =  "SELECT query_domain,COUNT(*) FROM queries "\
        "WHERE query_time BETWEEN '%s' AND '%s'"\
        "GROUP BY query_domain ORDER BY count(*) DESC LIMIT 50;"% (str(query_date)+":00:00", str(datetime.timedelta(hours=1)+datetime.datetime.strptime(query_date, '%Y-%m-%d %H')))
    print (sql)
    cursor.execute(sql)
    hourly_data = cursor.fetchall()

    sql = "SELECT COUNT(*) FROM queries "\
        "WHERE query_time BETWEEN '%s' AND '%s'"% (str(query_date)+":00:00", str(datetime.timedelta(hours=1)+datetime.datetime.strptime(query_date, '%Y-%m-%d %H')))
    cursor.execute(sql)
    total_amount = cursor.fetchone()[0]

    sql = "SELECT COUNT(DISTINCT(query_domain)) FROM queries "\
        "WHERE query_time BETWEEN '%s' AND '%s'"% (str(query_date)+":00:00", str(datetime.timedelta(hours=1)+datetime.datetime.strptime(query_date, '%Y-%m-%d %H')))
    cursor.execute(sql)
    count_distinct_domains = cursor.fetchone()[0]
    return {
        "traffic_duration": query_date, 
        "total_amount": total_amount,
        "distinct_domains": count_distinct_domains,
        "top_domain": [ 
                {"domain":i[0], "domain_traffic":i[1]} for i in list(hourly_data)
        ]
    }

def top_traffic_domain_day(query_date):
    sql =  "SELECT query_fld,COUNT(*) FROM queries "\
        "WHERE query_time BETWEEN '%s' AND '%s'"\
        "GROUP BY query_fld ORDER BY count(*) DESC LIMIT 100;"% (query_date, str(datetime.timedelta(days=1)+datetime.datetime.strptime(query_date, '%Y-%m-%d')).split()[0])

    cursor.execute(sql)
    daily_data = cursor.fetchall()
    sql = "SELECT COUNT(*) FROM queries "\
        "WHERE query_time BETWEEN '%s' AND '%s'"% (query_date, str(datetime.timedelta(days=1)+datetime.datetime.strptime(query_date, '%Y-%m-%d')).split()[0])
    cursor.execute(sql)
    total_amount = cursor.fetchone()[0]

    sql = "SELECT COUNT(DISTINCT(query_domain)) FROM queries "\
        "WHERE query_time BETWEEN '%s' AND '%s'"% (query_date, str(datetime.timedelta(days=1)+datetime.datetime.strptime(query_date, '%Y-%m-%d')).split()[0])
    cursor.execute(sql)
    count_distinct_domains = cursor.fetchone()[0]
    return {
        "traffic_duration": query_date, 
        "total_amount": total_amount,
        "distinct_domains": count_distinct_domains,
        "top_domain": [ 
            {"domain":i[0], "domain_traffic":i[1]} for i in list(daily_data)
        ]
    }

def insert_hourly_data_into_mongodb():
    sql = "SELECT DISTINCT DATE_FORMAT(query_time, '%%Y-%%m-%%d %%H') FROM queries WHERE query_time >'%s'"%str(datetime.timedelta(hours=1)+datetime.datetime.strptime(get_latest_hour(), '%Y-%m-%d %H'))
    cursor.execute(sql)
    query_dates = cursor.fetchall()
    res = []
    for query_date in query_dates:
        res.append(top_traffic_domain_hour(query_date[0]))
    if res:
        db.hourly_analysis.insert_many(res)

def insert_daily_data_into_mongodb():
    sql = "SELECT DISTINCT DATE_FORMAT(query_time, '%%Y-%%m-%%d') FROM queries WHERE query_time> '%s'"%str(datetime.timedelta(days=1)+datetime.datetime.strptime(get_latest_date(), '%Y-%m-%d'))
    cursor.execute(sql)
    query_dates = cursor.fetchall()
    res = []
    for query_date in query_dates:
        res.append(top_traffic_domain_day(query_date[0]))
    if res:
        db.daily_analysis.insert_many(res)


#def record_special_domain(domain, duration_flag, duration, amount):

def record_special_domain(domain):
    has_previous_record = db.special_domains.count_documents({'domain': domain})
    if not has_previous_record:
        res = {
            "domain" : domain,
            "child": [],
            "daily_history": [],
            "hourly_history": []
        }
        db.special_domains.insert_one(res)
    

if __name__ == "__main__":
    #insert_daily_data_into_mongodb()
    #insert_hourly_data_into_mongodb()
    record_special_domain("biadu.com")
