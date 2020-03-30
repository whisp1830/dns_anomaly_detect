package org.example;

import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.timestamps.BoundedOutOfOrdernessTimestampExtractor;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer010;
import org.apache.flink.table.api.EnvironmentSettings;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.java.StreamTableEnvironment;
import org.apache.flink.types.Row;

import java.util.Properties;

public class FullDomainCount {

    public static void main(String[] args) throws Exception {

        EnvironmentSettings fsSettings = EnvironmentSettings.newInstance().useOldPlanner().inStreamingMode().build();
        StreamExecutionEnvironment fsEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(fsEnv, fsSettings);
        fsEnv.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "localhost:9092");

        SingleOutputStreamOperator<Tuple3<Long, String, Integer>> source = fsEnv
                .addSource(new FlinkKafkaConsumer010<String>("queries", new SimpleStringSchema(), properties))
                .map(new MapFunction<String, Tuple3<Long, String, Integer>>() {
                    @Override
                    public Tuple3<Long, String, Integer> map(String s) throws Exception {
                        return new Tuple3<Long, String, Integer>(Long.parseLong(s.split(" ")[0]), s.split(" ")[1], 1);
                    }
                })
                .assignTimestampsAndWatermarks(
                        new BoundedOutOfOrdernessTimestampExtractor<Tuple3<Long, String, Integer>>(Time.seconds(1)){
                            @Override
                            public long extractTimestamp(Tuple3<Long, String, Integer> longStringIntegerTuple3) {
                                return longStringIntegerTuple3.f0 * 1000;
                            }
                        }
                );

        tableEnv.registerDataStream("tdns", source, "rowtime.rowtime, domain, amount");

        //result1 监控 full domain 的出现频率
        Table result1 = tableEnv.sqlQuery(
                "SELECT TUMBLE_START(rowtime, INTERVAL '1' MINUTE) as rstart, domain, SUM(amount) FROM tdns" +
                        " GROUP BY TUMBLE(rowtime, INTERVAL '1' MINUTE), domain");
        tableEnv.toRetractStream(result1, Row.class).print();
        fsEnv.execute("Window WordCount");
    }
}