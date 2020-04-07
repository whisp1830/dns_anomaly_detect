import datetime
import pymysql
import pymongo
import calendar
from dateutil import parser

connection = pymysql.connect(host='localhost',
                            port=3306,
                            user='root',
                            password='',
                            db='dns_flow',
                            charset='utf8')
print ("MySQL数据库连接成功")
cursor = connection.cursor()
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['domain_frequency']


def removeDuplicate(context):
    new_context = [context[0]]
    for i in range(1,len(context)):
        if context[i][1] != context[i-1][1]:
            new_context.append(context[i])
    return new_context

def getClientHistory(client_ip, table_name, cursor):
    sql = '''
        SELECT query_time, query_domain 
        FROM %s WHERE query_client_ip='%s' 
        '''%(table_name, client_ip)
    cursor.execute(sql)
    raw_history = cursor.fetchall()
    return raw_history

def recordContext(domain, context, db):
    db.domain_context.update_one(
        { "domain" : domain},
        {
            "$addToSet":{
                "context": {
                    "$each": context
                }
            }
        },
        upsert=True
    )

def getContext(domain, client_ip, table_name, cursor, db):
    client_history = getClientHistory(client_ip, table_name, cursor)
    rec, amount = 0, len(client_history)
    domain_contexts = []
    while rec < amount:
        if client_history[rec][1].endswith(domain):
            start = rec-5 if rec>4 else 0
            stop = rec+5 if rec<amount-5 else amount
            domain_contexts.append(removeDuplicate(client_history[start:stop]))
            rec += 5
        else:
            rec += 1
    recordContext(domain, domain_contexts, db)


getContext("ydy.com", "10.246.59.150", "queries_2020_01_07", cursor, db)