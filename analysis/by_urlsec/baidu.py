import os
import time
import pymysql
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

connection = pymysql.connect(host='127.0.0.1',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()

r = os.popen("which chromedriver")
chromedriver_path = r.read().strip()
r.close()
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
#chrome_options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败

driver = webdriver.Chrome(chromedriver_path, options=chrome_options)
# Optional argument, if not specified will search path.



def get_one(domain):
    url = "https://cn.bing.com/search?q=" + domain
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "lxml")
    res = ""
    try:
        res = soup.find_all('h2')[0].text
    except:
        pass
    return res
    

cursor.execute(
    '''
        SELECT domain FROM domain_white_list
    '''
)

safe_domain = cursor.fetchall()

count = 1
for domain in safe_domain[10000:]:
    domain = domain[0]
    note = get_one(domain)
    try:
        cursor.execute(
            '''
            UPDATE domain_white_list
            SET note=%s WHERE domain=%s
            ''',
            (note, domain)
        )
    except:
        pass
    count += 1
    if count % 100 == 0:
        connection.commit()
        print (count)
    print (note, domain)
connection.commit()

    
