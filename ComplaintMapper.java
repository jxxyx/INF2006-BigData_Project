package Twitterairlinetask3;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class ComplaintMapper extends Mapper<Object, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text country = new Text();

    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString();
        String[] fields = line.split("\\t"); // Assuming the dataset is tab-separated

        // Column indices (adjust if needed)
        int countryColumnIndex = 10; // _country
        int sentimentColumnIndex = 14; // airline_sentiment
        int negativeColumnIndex = 15;

        // Check if the line contains enough columns
        if (fields.length > Math.max(countryColumnIndex, sentimentColumnIndex)) {
            String countryName = fields[countryColumnIndex].trim();
            String sentiment = fields[sentimentColumnIndex].trim().toLowerCase();

            // Emit only if sentiment is negative and country is not empty
            if (!countryName.isEmpty() && !sentiment.isEmpty() && "negative".equals(sentiment)) {
                country.set(countryName);
                context.write(country, one);

            }
        }
    }
}
