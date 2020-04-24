import pymysql

connection = pymysql.connect(host='localhost',
                        port=3306,
                        user='root',
                        password='',
                        database='dns_flow')
cursor = connection.cursor()
print ("数据库连接成功")

cursor.execute("SELECT DISTINCT query_fld FROM queries")
domains = cursor.fetchall()
count = 0
for domain in domains:
    try:
        sql = '''
            INSERT INTO domain_first_seen 
            SELECT query_fld, MIN(query_time)
            FROM queries
            WHERE query_fld=%s
        '''
        cursor.execute(sql, domain[0])
        count += 1
        print (count)
    except:
        pass
connection.commit()