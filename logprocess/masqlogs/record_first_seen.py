import pymysql

connection = pymysql.connect(host='localhost',
                        port=3306,
                        user='root',
                        password='',
                        database='dns_flow')
cursor = connection.cursor()
print ("数据库连接成功")


def get_distinct_fld(cursor):
    sql = "SELECT DISTINCT query_fld FROM queries WHERE query_fld NOT IN "\
        "(SELECT domain FROM domain_white_list)"\
        "AND query_fld NOT IN (SELECT domain FROM domain_first_seen)"
    cursor.execute(sql)
    res = cursor.fetchall()
    return res

for record in get_distinct_fld(cursor):
    domain = record[0]
    print (domain)
    sql = '''
        INSERT INTO domain_first_seen 
        SELECT query_fld, MIN(query_time)
        FROM queries
        WHERE query_fld=%s
    '''
    cursor.execute(sql ,domain)
connection.commit()