import shodan

SHODAN_API_KEY = "vsdv6Ba1aabqZdTT3VsIBuVYtc4pJA2r"
api = shodan.Shodan(SHODAN_API_KEY)

host = api.host("149.129.126.92")

print (host["country_code"])
print (host["org"])
print (host["latitude"])
print (host["longitude"])
print (host["isp"])
print (host["asn"])
print (host["ports"])