import requests
from bs4 import BeautifulSoup
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

for i in range(1,21):
    if i == 1:
        url = "https://alexa.chinaz.com/Country/index_CN.html"
    else:
        url = "https://alexa.chinaz.com/Country/index_CN_%s.html"%str(i)
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'html.parser')
    sites = soup.find_all(attrs = { "class":"righttxt"})
    for site in sites:
        try:
            cursor.execute('INSERT INTO domain_white_list(domain) VALUES(%s)', str(site.a.text).lower())
        except:
            pass
connection.commit()