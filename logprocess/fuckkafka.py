from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
value = input()
future = producer.send('queries' , key= b'my_key', value= bytes(value, encoding="utf-8"), partition= 0)
result = future.get(timeout= 10)
print(result)
