package airlinemeanmedian;

import java.io.IOException;
import java.util.*;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * MapReduce program to calculate statistical measures (mean, median, std dev) of trust scores
 * for different communication channels in airline data.
 *
 * Input: Tab-separated file containing airline communication data
 * Required columns:
 * - Column H (index 7): Communication channel
 * - Column I (index 8): Trust score
 *
 * Output: Statistical analysis for each communication channel including:
 * - Mean trust score
 * - Median trust score
 * - Standard deviation
 * - Sample size
 * - Min and max scores
 */
public class TrustScoreStatistics {

    /**
     * Mapper class that processes input records and emits channel-score pairs
     * Key: Communication channel (Text)
     * Value: Trust score (DoubleWritable)
     */
    public static class ScoreMapper extends Mapper<Object, Text, Text, DoubleWritable> {
        private Text channel = new Text();
        private DoubleWritable score = new DoubleWritable();

        @Override
        public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
            // Skip header row
            if (value.toString().startsWith("unit_id")) return;

            String[] fields = value.toString().split("\t");

            try {
                // Extract channel (column H) and trust score (column I)
                String communicationChannel = fields[7].trim();
                double trustScore = Double.parseDouble(fields[8].trim());

                // Validate data before emitting
                if (!communicationChannel.isEmpty() && trustScore >= 0) {
                    // Remove any surrounding quotes from channel name
                    communicationChannel = communicationChannel.replaceAll("^\"|\"$", "");
                    channel.set(communicationChannel);
                    score.set(trustScore);
                    context.write(channel, score);
                }
            } catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
                // Track invalid records using counter
                context.getCounter("Map", "Invalid_Records").increment(1);
            }
        }
    }

    /**
     * Reducer class that calculates statistical measures for each channel
     * Input: Channel name and all associated trust scores
     * Output: Formatted statistical analysis including mean, median, and other measures
     */
    public static class StatisticsReducer extends Reducer<Text, DoubleWritable, Text, Text> {

        @Override
        public void reduce(Text key, Iterable<DoubleWritable> values, Context context)
                throws IOException, InterruptedException {

            // Store all scores for statistical calculations
            List<Double> scores = new ArrayList<>();
            double sum = 0;
            int count = 0;

            // Collect scores and calculate sum
            for (DoubleWritable val : values) {
                double score = val.get();
                scores.add(score);
                sum += score;
                count++;
            }

            if (count > 0) {
                // Calculate mean
                double mean = sum / count;

                // Calculate median
                Collections.sort(scores);
                double median;
                if (count % 2 == 0) {
                    // For even number of scores, average the middle two
                    median = (scores.get(count/2 - 1) + scores.get(count/2)) / 2.0;
                } else {
                    // For odd number of scores, take the middle one
                    median = scores.get(count/2);
                }

                // Calculate standard deviation
                double sumSquaredDiff = 0;
                for (double score : scores) {
                    sumSquaredDiff += Math.pow(score - mean, 2);
                }
                double stdDev = Math.sqrt(sumSquaredDiff / count);

                // Format output with all statistical measures
                String stats = String.format("Channel: %s\n" +
                                "  Mean Trust Score: %.4f\n" +
                                "  Median Trust Score: %.4f\n" +
                                "  Standard Deviation: %.4f\n" +
                                "  Sample Size: %d\n" +
                                "  Min Score: %.4f\n" +
                                "  Max Score: %.4f",
                        key.toString(),
                        mean,
                        median,
                        stdDev,
                        count,
                        scores.get(0),          // Min score (after sorting)
                        scores.get(count - 1)    // Max score (after sorting)
                );

                context.write(new Text(key), new Text(stats));
            }
        }
    }

    /**
     * Main method to configure and run the MapReduce job
     * Arguments:
     * args[0]: Input path
     * args[1]: Output path
     */
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "trust score statistics");

        // Set job classes
        job.setJarByClass(TrustScoreStatistics.class);
        job.setMapperClass(ScoreMapper.class);
        job.setReducerClass(StatisticsReducer.class);

        // Set output types for mapper
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(DoubleWritable.class);

        // Set output types for reducer
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        // Set input and output paths
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        // Run the job
        boolean success = job.waitForCompletion(true);

        if (success) {
            // Run the analysis on the output
            ResultAnalyzer.analyzeResults(args[1]);
        }

        System.exit(success ? 0 : 1);
    }
}