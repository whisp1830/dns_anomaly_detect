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
    WHERE query_fld NOT IN
    (
        SELECT domain FROM
        domain_white_list
    )
    ''')

distinct_fld = cursor.fetchall()

with open("tobechecked.txt", "w") as f:
    for i in distinct_fld:
        f.write(i[0] + "\n")
