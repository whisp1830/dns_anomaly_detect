import os
import pymysql


connection = pymysql.connect(host='localhost',
                    port=3306,
                    user='root',
                    password='',
                    db='dns_flow',
                    charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()


connection = pymysql.connect(host='106.15.250.172',
                    port=3306,
                    user='root',
                    password='069879ea8f',
                    db='dns_flow',
                    charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()
def is_polluted(domain):
    command = "dig @a.root-servers.net. %s | grep %s"%(domain, domain)
    tmp = os.popen(command)
    res = tmp.read().splitlines()
    print (res)
    return False if len(res) == 2 else True


if __name__ == "__main__":
    cursor.execute(
        '''
            SELECT distinct query_fld from queries_2020_01_07
        '''
    )
    domains = cursor.fetchall()
    with open("hehe","w") as f:
        for d in domains:
            f.write(d[0] + '\n')
