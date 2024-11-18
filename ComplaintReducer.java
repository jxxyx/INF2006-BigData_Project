package Twitterairlinetask3;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;
import java.util.*;

public class ComplaintReducer extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final Map<String, Integer> countryCounts = new HashMap<>();

    @Override
    public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
        int sum = 0;

        // Aggregate the counts for each country
        for (IntWritable val : values) {
            sum += val.get();
        }

        // Store the aggregated count in the map
        countryCounts.put(key.toString(), sum);
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        //Write header first
        context.write(new Text("Country\tCount"), null);

        // Sort the map by values (descending order)
        List<Map.Entry<String, Integer>> sortedEntries = new ArrayList<>(countryCounts.entrySet());
        sortedEntries.sort((e1, e2) -> e2.getValue().compareTo(e1.getValue()));

        // Write the sorted results to the context
        for (Map.Entry<String, Integer> entry : sortedEntries) {
            context.write(new Text(entry.getKey()), new IntWritable(entry.getValue()));
        }
    }
}
