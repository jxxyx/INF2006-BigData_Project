package Twitterairlinetask3;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import java.io.IOException;

public class ComplaintMapper extends Mapper<Object, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text country = new Text();

    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        // Split the line by tab
        String[] fields = value.toString().split("\\t");

        // Ensure there are enough fields in the record
        if (fields.length > 15) {
            String sentiment = fields[14]; // Sentiment column
            String countryField = fields[10]; // Country column

            if ("negative".equalsIgnoreCase(sentiment) && !countryField.isEmpty()) {
                country.set(countryField);
                context.write(country, one);
            }
        }
    }
}
