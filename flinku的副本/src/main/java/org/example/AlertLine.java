package org.example;

import java.util.HashMap;
import com.mongodb.MongoClient;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;


public class AlertLine {
    public HashMap<String, Integer> alertValues;
    private MongoClient mongoClient;
    private MongoDatabase mongoDatabase;

    public AlertLine(String s) {
        alertValues = new HashMap<>();
        // 连接到 mongodb 服务
        mongoClient = new MongoClient( "localhost" , 27017 );

        // 连接到数据库
        mongoDatabase = mongoClient.getDatabase("domain_frequency");
        System.out.println("Connect to database successfully");

        MongoCollection<Document> collection = mongoDatabase.getCollection("domain_control");
        FindIterable<Document> documents = collection.find();
        MongoCursor<Document> iterator = documents.iterator();
        while (iterator.hasNext()) {
            Document singleLimit = iterator.next();
            String domain = singleLimit.get("domain").toString();
            Integer limit = Integer.parseInt(singleLimit.get("limit").toString());
            alertValues.put(domain, limit);
        }
        alertValues.forEach((k,v) -> System.out.println("key: "+k+" value:"+v));
        System.out.println("初始化完成");
    }

    int getLine(String domain){
        return alertValues.get(domain);
    }

}
