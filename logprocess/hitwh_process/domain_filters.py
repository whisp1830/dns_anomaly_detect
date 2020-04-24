import pymysql
from bloom_filter import BloomFilter

def get_safe_domain_filter(max_elements, error_rate, filename, cursor):
    safe_domain_filter = BloomFilter(
        max_elements = max_elements, 
        error_rate = error_rate, 
        filename= filename
    )
    if not cursor and '360.cn' in safe_domain_filter and 'baidu.com' in safe_domain_filter:
        print ("装填完毕！  ")
        return safe_domain_filter
    cursor.execute("SELECT domain FROM domain_white_list")
    for i in cursor.fetchall():
        safe_domain_filter.add(i[0])
    return safe_domain_filter

def get_black_domain_filter(cursor):
    cursor.execute("SELECT domain FROM domain_black_list")
    return tuple([ i[0] for i in cursor.fetchall()])
