import sys
import pymongo
from tld import get_fld
from domain_filters import *

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['domain_frequency']
print ("MongoDB数据库连接成功")

safe_domain_filter = get_safe_domain_filter(
    max_elements=100000, 
    error_rate=0.1, 
    filename="/Users/whisp/Mycode/dns_anomaly_detect/logprocess/hitwh_process/safe_domain.filter",
    cursor=None
    )

count = 1
res = []
with open("log20.log", "r") as f:
    single_answer = f.readline().replace(";", " ").split()
    while single_answer:
        try:
            domain_fld = get_fld(single_answer[9], fix_protocol=True)
            if domain_fld not in safe_domain_filter:
                start = single_answer.index("Response:")
                single_answer = single_answer[start:]
                single_res = []
                for i in range(len(single_answer)-2):
                    if len(single_answer[1])<50 and single_answer[i] == 'IN' and single_answer[i+1] == 'A':
                        ip = single_answer[i+2]
                        single_res.append(ip)
                        count += 1
                res.append((domain_fld, single_res))
        except:
            pass

        print (count)

        if count % 10000 == 0:
            print ("开始写入数据库")
            for i in res:
                db.domain_control.update_one(
                    { "domain" : i[0]},
                    {
                        "$addToSet":{
                            "ips": { 
                                "$each" : i[1]
                            }
                        }
                    },
                    upsert=True
                )
            res = []
            print (count)
        single_answer = f.readline().replace(";", " ").split()
