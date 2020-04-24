import geoip2.database

reader = geoip2.database.Reader('/Users/whisp/Mycode/dns_anomaly_detect/analysis/by_location/GeoLite2-City.mmdb')
response = reader.city('149.129.126.92')

print (response.country.name)
print (response.city.name)
print (response.traits.network)