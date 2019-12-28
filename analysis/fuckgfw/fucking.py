import dns.resolver

myResolver = dns.resolver.Resolver()
myResolver.nameservers = ['114.114.114.114']

res = set()

for _ in range(1000):
    print (_)
    myAnswers = myResolver.query("google.com", "A")
    for answer in myAnswers:
        res.add(answer)

with open("fuckyouleatherman.txt","a") as f:
    for i in res:
        f.write( str(i) + "\n")