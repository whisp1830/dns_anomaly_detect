import pymysql
connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
print ("数据库连接成功")
cursor = connection.cursor()

cursor.execute('''
    SELECT DISTINCT query_fld
    FROM queries
    ''')

distinct_fld = cursor.fetchall()
for i in distinct_fld:
    print (i[0])
