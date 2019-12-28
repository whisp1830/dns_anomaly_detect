import tld
import pymysql

with open("cnblocklist.txt","r") as f:
    fuck = f.readlines()


seto = set()
count = 0
for f in fuck:
    if "Whitelist Start" in f:
        break
    f = f.strip(" |?!@#$%^&*:.~`-=+\n")
    if "http://" not in f:
        f += "http://" + f
    try:
        tmp = tld.get_fld(f)
        print (tmp)
        seto.add(tmp)
        count += 1
    except:
        print (f + " failed")
        pass
print (count)
print (len(seto))

connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
cursor = connection.cursor()
for s in seto:
    sql = "INSERT INTO domain_block_list(domain) VALUES('%s')"%s
    print (sql)
    try:
        cursor.execute(sql)
    except:
        pass
connection.commit()

