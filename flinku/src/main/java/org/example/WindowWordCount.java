package org.example;

import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.timestamps.BoundedOutOfOrdernessTimestampExtractor;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer010;

import java.util.Properties;

public class WindowWordCount {

    public static void main(String[] args) throws Exception {

        AlertLine al = new AlertLine("hey");

        System.out.println(al.getLine("baidu.com"));
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "localhost:9092");

        DataStream<String> source = env
                .addSource(new FlinkKafkaConsumer010<String>("queries", new SimpleStringSchema(), properties));

        DataStream<Tuple3<Long, String, Integer>> counts = source.map(new MapFunction<String, Tuple3<Long, String, Integer>>() {
            @Override
            public Tuple3<Long, String, Integer> map(String s) throws Exception {
                return new Tuple3<Long, String, Integer>(Long.parseLong(s.split(" ")[0]), s.split(" ")[1], 1);
            }
            }).assignTimestampsAndWatermarks(
                new BoundedOutOfOrdernessTimestampExtractor<Tuple3<Long, String, Integer>>(Time.seconds(1)){
                    @Override
                    public long extractTimestamp(Tuple3<Long, String, Integer> longStringIntegerTuple3) {
                        return longStringIntegerTuple3.f0 * 1000;
                    }
                }
                ).keyBy(1)
                .window(SlidingEventTimeWindows.of(Time.minutes(1), Time.seconds(30)))
                .sum(2)
                .filter((FilterFunction<Tuple3<Long, String, Integer>>) value -> value.f2 > 5);

        counts.print();
        env.execute("Window WordCount");
    }
}