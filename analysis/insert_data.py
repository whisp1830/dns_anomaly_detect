import pymysql

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
    print ("you")