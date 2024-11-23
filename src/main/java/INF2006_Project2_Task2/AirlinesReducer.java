package INF2006_Project2_Task2;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;

// 2302997
// Mock Jun Yu

public class AirlinesReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private Map<String, PriorityQueue<Map.Entry<String, Integer>>> airlineReasonMap = new HashMap<>();
    private boolean headerWritten = false; // To ensure the header is written only once

    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
        // Split the key to extract airline and reason
        String[] keys = key.toString().split(":");
        String airline = keys[0];
        String reason = keys[1];

        // Sum up occurrences for this specific airline-reason pair
        int count = 0;
        for (IntWritable val : values) {
            count += val.get();
        }

        // Use a priority queue to keep the top 5 reasons per airline
        airlineReasonMap.putIfAbsent(airline, new PriorityQueue<>((a, b) -> Integer.compare(a.getValue(), b.getValue())));
        airlineReasonMap.get(airline).add(new HashMap.SimpleEntry<>(reason, count));

        // If the priority queue has more than 5 items, remove the lowest one
        if (airlineReasonMap.get(airline).size() > 5) {
            airlineReasonMap.get(airline).poll();
        }
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        // Write the header to the output file
        if (!headerWritten) {
            context.write(new Text("Airline\tReason\tCount"), null); // Write the header as tab-separated
            headerWritten = true;
        }

        // Output the top 5 reasons for each airline
        for (Map.Entry<String, PriorityQueue<Map.Entry<String, Integer>>> entry : airlineReasonMap.entrySet()) {
            String airline = entry.getKey();
            PriorityQueue<Map.Entry<String, Integer>> reasonsQueue = entry.getValue();

            // Output each reason and its count
            while (!reasonsQueue.isEmpty()) {
                Map.Entry<String, Integer> reasonCount = reasonsQueue.poll();
                String outputKey = airline + "\t" + reasonCount.getKey(); // Format as tab-separated values
                context.write(new Text(outputKey), new IntWritable(reasonCount.getValue()));
            }
        }
    }
}
