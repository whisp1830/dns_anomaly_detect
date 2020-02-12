import ip2region

searcher = ip2region.Ip2Region("ip2Region.db")

ips = []
with open("distinctips.txt","r") as f: 
    ips = f.readlines()

for ip in ips:
    ip = ip.strip().strip('"')
    if ip: 
        result = searcher.memorySearch(ip)
        region = str(result['region'], encoding="utf-8")
        print (ip + " " +region)