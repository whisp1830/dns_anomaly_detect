from kafka import KafkaConsumer

consumer = KafkaConsumer('wiki-result', bootstrap_servers= ['localhost:9092'])
for msg in consumer:
    print(msg)