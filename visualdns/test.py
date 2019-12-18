import pymysql
from tld import get_fld
connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='',
                             db='dns_flow',
                             charset='utf8')
print ("数据库连接成功")
# 获取游标
cursor = connection.cursor()

with open("top500Domains.csv","r") as f:
    sites = f.readlines()[1:]
for site in sites:
    site = get_fld(site.split(",")[1].strip('"'), fail_silently=True, fix_protocol=True)
    try:
        cursor.execute('INSERT INTO domain_white_list(domain) VALUES(%s)', site)
    except:
        pass
connection.commit()