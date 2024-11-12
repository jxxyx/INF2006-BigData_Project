package Project2_Task5;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

public class SentimentReducer extends Reducer<Text, Text, Text, Text> {
    private int correctPredictions = 0;
    private int totalPredictions = 0;

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
        for (Text value : values) {
            String[] fields = value.toString().split("\\t");

            if (fields.length == 3) {
                String actualSentiment = fields[0];
                String predictedSentiment = fields[2];

                // Filter out "unknown" rows from evaluation
                if ("unknown".equals(actualSentiment)) {
                    continue;
                }

                // Check if prediction matches the actual sentiment
                if (actualSentiment.equals(predictedSentiment)) {
                    correctPredictions++;
                }
                totalPredictions++;

                // Output each tweet's info along with correctness (correct/incorrect)
                String correctness = actualSentiment.equals(predictedSentiment) ? "correct" : "incorrect";
                context.write(key, new Text(fields[0] + "\t" + fields[1] + "\t" + fields[2] + "\t" + correctness));
            }
        }
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        // Calculate accuracy and ensure it's within bounds [0,1]
        double accuracy = (totalPredictions > 0) ? (double) correctPredictions / totalPredictions : 0.0;
        context.write(new Text("Overall Accuracy"), new Text(String.format("%.4f", accuracy)));
    }
}
