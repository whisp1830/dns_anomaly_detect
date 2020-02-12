import shodan

SHODAN_API_KEY = "vsdv6Ba1aabqZdTT3VsIBuVYtc4pJA2r"

api = shodan.Shodan(SHODAN_API_KEY)

# Lookup the host
host = api.host('149.129.126.92')

# Print general info
print("""
        IP: {}
        Organization: {}
        Operating System: {}
""".format(host['ip_str'], host.get('org', 'n/a'), host.get('os', 'n/a')))

# Print all banners
for item in host['data']:
        print("""
                Port: {}
                Banner: {}

        """.format(item['port'], item['data']))