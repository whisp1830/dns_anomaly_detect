import pymysql
import pymongo
import geoip2.database

class Connector():
    def __init__(self):
        self.connection = pymysql.connect(host='localhost',
                        port=3306,
                        user='root',
                        password='',
                        db='dns_flow',
                        charset='utf8')
        print ("MySQL数据库连接成功")
        self.cursor = self.connection.cursor()
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['domain_frequency']
        print ("MongoDB数据库连接成功")

        sql = "SELECT domain, note FROM domain_black_list"
        self.cursor.execute(sql)
        tmp = self.cursor.fetchall()
        self.domain_black_list = set([i[0] for i in tmp])
        self.black_note = {}
        for t in tmp:
            self.black_note[t[0]] = t[1]

        sql = "SELECT domain, note FROM domain_white_list"
        self.cursor.execute(sql)
        tmp = self.cursor.fetchall()
        self.domain_white_list = set([i[0] for i in tmp])
        self.white_note = {}
        for t in tmp:
            self.white_note[t[0]] = t[1]
        self.city_locate = geoip2.database.Reader('/Users/whisp/Mycode/dns_anomaly_detect/analysis/by_location/GeoLite2-City.mmdb')
        self.asn_locate = geoip2.database.Reader('/Users/whisp/Mycode/dns_anomaly_detect/analysis/by_location/GeoLite2-ASN.mmdb')

if __name__ == "__main__":
    c = Connector()
    print ('pornoshara.tv' in c.domain_black_list)
    print ('baidu.com' in c.domain_white_list)