import os
import sys
import time
import pymysql
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

connection = pymysql.connect(host='106.15.250.172',
                            port=3306,
                            user='root',
                            password='069879ea8f',
                            db='dns_flow',
                            charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()

filename = "拉清单.txt"
r = os.popen("which chromedriver")
chromedriver_path = r.read().strip()
r.close()
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--hide-scrollbars') #隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
chrome_options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这>条会启动失败

driver = webdriver.Chrome(chromedriver_path, options=chrome_options)

def work():
    counter = 1
    with open(filename,"r") as f:
        url = f.readline().strip()
        while url:
            driver.get("https://urlsec.qq.com/check.html?url=" + url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source,"lxml")
            res = soup.find('div', attrs={"class":"result"})

            if "危险" in str(res):
                    print (str(counter) + " /6000 " + url + " 危险")
                    note = soup \
                        .find('ul', attrs={"class":"result-warning-list"}) \
                        .find_all('span')[1] \
                        .text
                    sql = "INSERT INTO domain_black_list(domain, note) VALUES(%s, %s)"
                    cursor.execute(sql, (url, note))
                    connection.commit()
            else:
                    print (str(counter) + " /6000 " + url + " 安全")
            url = f.readline().strip()
            counter += 1
    driver.quit()

if __name__ == "__main__":
    work()

