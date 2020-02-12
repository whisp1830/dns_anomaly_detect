import os
import sys
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

filename = "tobechecked.txt"
r = os.popen("which chromedriver")
chromedriver_path = r.read().strip()
r.close() 
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--hide-scrollbars') #隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
chrome_options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败

driver = webdriver.Chrome(chromedriver_path, options=chrome_options) 

with open(filename,"r") as f:
    for _ in range(3):
        url = f.readline().strip() 
        driver.get("https://urlsec.qq.com/check.html?url=" + url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source,"lxml")
        res = soup.find('div', attrs={"class":"result"})
        if "危险" in str(res):
            print (url + " 危险")
        else:
            print (url + " 安全")

driver.quit()
