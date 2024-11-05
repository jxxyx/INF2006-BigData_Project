import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class TwitterMapper extends Mapper<Object, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text airline = new Text();

    // Keywords to look for in delay-related tweets
    private static final String[] DELAY_KEYWORDS = {"delay", "delayed", "late flight"};

    @Override
    protected void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        // Split the line on commas, but ignore commas within quotes
        String[] fields = value.toString().split(",");

        // Ensure there are enough fields in each row (at least 24 based on the structure you shared)
        if (fields.length < 24) {
            return;
        }

        // Extract relevant fields
        String sentiment = fields[14].toLowerCase(); // airline_sentiment
        String negativeReason = fields[15].toLowerCase(); // negativereason
        String airlineName = fields[16]; // airline
        String tweetText = fields[21].toLowerCase(); // text

        // Filter for negative tweets mentioning delays
        if ("negative".equals(sentiment) && (negativeReason.contains("delay") || containsDelayKeyword(tweetText))) {
            airline.set(airlineName);
            context.write(airline, one); // Emit airline name and count of 1
        }
    }

    private boolean containsDelayKeyword(String text) {
        for (String keyword : DELAY_KEYWORDS) { //for each keyword in the list called DELAY_KEYWORDS
            if (text.contains(keyword)) { //if the text contains the keyword
                return true; 	            //return
            }
        }
        return false;
    }
}
