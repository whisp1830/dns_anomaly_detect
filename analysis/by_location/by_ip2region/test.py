import ip2region

searcher = ip2region.Ip2Region("ip2Region.db")

ips = [
    '1.1.1.1',
    '8.8.8.8'
]


for ip in ips:
    ip = ip.strip().strip('"')
    if ip: 
        result = searcher.memorySearch(ip)
        region = str(result['region'], encoding="utf-8")
        print (ip + " " +region)