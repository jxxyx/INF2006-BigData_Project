package Project2_Task5;

import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.HashSet;
import java.util.Set;

public class SentimentMapper extends Mapper<LongWritable, Text, Text, Text> {
    private Text tweetId = new Text();
    private Set<String> stopWords = new HashSet<>();

    @Override
    protected void setup(Context context) throws IOException, InterruptedException {
        // Load SentiWordNet
        SentimentUtils.loadSentiWordNet();

        // Load stop words but retain some contextually important ones
        stopWords = loadStopWords("nltk_stopwords.txt");
        stopWords.remove("not"); // Retain "not" as it impacts sentiment
        stopWords.remove("very"); // Retain "very" as it intensifies sentiment
        stopWords.remove("never"); // Retain "never" as it indicates negation
    }

    private Set<String> loadStopWords(String fileName) throws IOException {
        Set<String> stopWords = new HashSet<>();
        InputStream inputStream = getClass().getResourceAsStream("/" + fileName);

        if (inputStream == null) {
            throw new IOException("Stop words file not found: " + fileName);
        }

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            String line;
            while ((line = reader.readLine()) != null) {
                stopWords.add(line.trim());
            }
        }

        return stopWords;
    }

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String[] fields = value.toString().split("\\t");

        // Ensure sufficient fields in TSV format
        if (fields.length >= 27) {
            String airlineSentimentGold = fields[17].trim();  // Column for actual sentiment
            String tweetText = fields[21].trim();             // Column for tweet text
            String tweetIdStr = fields[24].trim();            // Column for tweet ID

            // Handle missing sentiment labels
            if (airlineSentimentGold.isEmpty()) {
                airlineSentimentGold = "unknown";
            }

            // Preprocess text: lowercase, remove non-alphabet characters, and keep relevant stop words
            tweetText = tweetText.toLowerCase().replaceAll("[^a-z\\s]", "");
            StringBuilder filteredText = new StringBuilder();
            for (String word : tweetText.split("\\s+")) {
                if (!stopWords.contains(word)) {
                    filteredText.append(word).append(" ");
                }
            }

            // Predict sentiment with improved analysis in SentimentUtils
            String predictedSentiment = SentimentUtils.analyzeSentiment(filteredText.toString().trim());

            // Emit tweet ID as the key and sentiment info as the value
            tweetId.set(tweetIdStr);
            context.write(tweetId, new Text(airlineSentimentGold + "\t" + tweetText + "\t" + predictedSentiment));
        }
    }
}
