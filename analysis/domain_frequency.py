import pymysql
import pymongo
import calendar
from datetime import *
from dateutil.rrule import *
from dateutil.parser import *
from dateutil.relativedelta import *

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
    latest_hour = db.hourly_analysis.find({}, {'_id':0, 'traffic_duration':1}).sort("traffic_duration",-1).limit(1)[0]
    return latest_hour['traffic_duration']

def get_latest_date():
    latest_date = db.daily_analysis.find({}, {'_id':0, 'traffic_duration':1}).sort("traffic_duration",-1).limit(1)[0]
    return latest_date['traffic_duration']

def top_traffic_domain_hour(query_date):
    sql =  "SELECT query_domain,COUNT(*) FROM queries "\
        "WHERE DATE_FORMAT(query_time, '%%Y-%%m-%%d %%H') = '%s'"\
        "GROUP BY query_domain ORDER BY count(*) DESC LIMIT 20;"%query_date

    cursor.execute(sql)
    hourly_data = cursor.fetchall()
    sql = "SELECT COUNT(*) FROM queries "\
        "WHERE DATE_FORMAT(query_time, '%%Y-%%m-%%d %%H ') = '%s'"%query_date
    print (sql)
    cursor.execute(sql)
    total_amount = cursor.fetchone()[0]
    return {
        "traffic_duration": query_date, 
        "total_amount": total_amount,
        "top_domain": 
            [ 
                {"domain":i[0], "domain_traffic":i[1]} for i in list(hourly_data)
            ]
    }

def top_traffic_domain_day(query_date):
    sql =  "SELECT query_domain,COUNT(*) FROM queries "\
        "WHERE DATE_FORMAT(query_time, '%%Y-%%m-%%d') = '%s'"\
        "GROUP BY query_domain ORDER BY count(*) DESC LIMIT 50;"%query_date.split(" ")[0]
    print (sql)
    cursor.execute(sql)
    daily_data = cursor.fetchall()
    return {"traffic_duration": query_date, "top_domain": [ {"domain":i[0], "domain_traffic":i[1]} for i in list(daily_data)]}

def insert_hourly_data_into_mongodb():
    sql = "SELECT DISTINCT DATE_FORMAT(query_time, '%%Y-%%m-%%d %%H ') FROM queries WHERE DATE_FORMAT(query_time, '%%Y-%%m-%%d %%H ') > '%s'"%get_latest_hour()
    cursor.execute(sql)
    query_dates = cursor.fetchall()
    res = []
    for query_date in query_dates:
        res.append(top_traffic_domain_hour(query_date[0]))
    
    db.hourly_analysis.insert_many(res)

def insert_daily_data_into_mongodb():
    intervals = list(rrule(DAILY,dtstart=parse(get_latest_date())+relativedelta(days=-60),until=parse(get_latest_date())))
    sql = "SELECT DISTINCT DATE_FORMAT(query_time, '%%Y-%%m-%%d') FROM queries WHERE DATE_FORMAT(query_time, '%%Y-%%m-%%d') > '%s'"%get_latest_date()
    cursor.execute(sql)
    query_dates = cursor.fetchall()
    res = []
    for query_date in query_dates:
        res.append(top_traffic_domain_day(query_date[0]))
    
    db.daily_analysis.insert_many(res)


if __name__ == "__main__":
    insert_daily_data_into_mongodb()
    insert_hourly_data_into_mongodb()
