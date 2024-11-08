package INF2006_Project2_Task2;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;
import java.io.StringReader;

public class AirlinesMapper extends Mapper<Object, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text airlineReason = new Text();

    @Override
    protected void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        // Configure CSV parser for TSV format
        CSVFormat csvFormat = CSVFormat.DEFAULT
                .withDelimiter('\t') // Set delimiter to tab for TSV
                .withIgnoreEmptyLines()
                .withTrim()
                .withQuote('"')
                .withIgnoreSurroundingSpaces();

        try {
            // Parse the single line
            CSVParser parser = csvFormat.parse(new StringReader(value.toString()));
            CSVRecord record = parser.iterator().next(); // Get the first (and only) record

            // Verify we have enough columns
            if (record.size() >= 17) {
                String sentiment = record.get(14).trim().toLowerCase();
                String reason = record.get(15).trim();
                String airline = record.get(16).trim();

                // Only process records with negative sentiment and valid airline/reason
                if ("negative".equals(sentiment) && !airline.isEmpty() && !reason.isEmpty()) {
                    airlineReason.set(airline + ":" + reason);
                    context.write(airlineReason, one);
                }
            }
        } catch (Exception e) {
            // Log the error and continue processing other records
            System.err.println("Error processing record: " + value.toString());
            System.err.println("Error details: " + e.getMessage());
        }
    }
}
