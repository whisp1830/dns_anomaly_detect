import json
import requests
from bs4 import BeautifulSoup

def ip2region_138(url):
    '''
    根据ip138.com的数据，返回IP位置和归属信息
    url : str
    '''
    url = "http://www.ip138.com/iplookup.asp?ip=" + url
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "lxml")
    res = soup.find('ul', attrs={"class":"ul1"})
    for item in res:
        return item.text

def discover_subdomains_myssl(url):
    url = "https://myssl.com/api/v1/discover_sub_domain?domain=" + url
    r = requests.get(url)
    r = json.loads(r.text)
    return r['data']
if __name__ == "__main__":
    #print (ip2region_138("8.8.8.8"))
    for i in discover_subdomains_myssl("taobao.com"):
        print (i)