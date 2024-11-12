package Project2_Task5;

import java.io.*;
import java.util.HashMap;
import java.util.Map;

public class SentimentUtils {
    private static Map<String, Double[]> sentiWordNetMap = new HashMap<>();

    // Load SentiWordNet data into memory
    public static void loadSentiWordNet() throws IOException {
        InputStream inputStream = SentimentUtils.class.getResourceAsStream("/SentiWordNet_3.0.0.txt");
        if (inputStream == null) {
            throw new FileNotFoundException("SentiWordNet file not found in resources.");
        }

        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
        String line;

        while ((line = reader.readLine()) != null) {
            if (line.startsWith("#") || line.trim().isEmpty()) continue;

            String[] data = line.split("\\t");
            if (data.length < 5) continue;

            String pos = data[0];
            try {
                double posScore = Double.parseDouble(data[2]);
                double negScore = Double.parseDouble(data[3]);
                String synsetTerms = data[4];

                for (String term : synsetTerms.split(" ")) {
                    String[] termSplit = term.split("#");
                    String word = termSplit[0] + "#" + pos;
                    sentiWordNetMap.put(word, new Double[]{posScore, negScore});
                }
            } catch (NumberFormatException e) {
                System.err.println("Skipping line due to parse error: " + line);
            }
        }
        reader.close();
    }

    // Enhanced sentiment analysis with negation handling and adjustable threshold
    public static String analyzeSentiment(String text) {
        double posTotal = 0.0, negTotal = 0.0;
        int wordCount = 0;
        boolean negate = false;  // Track if the sentiment should be negated

        for (String word : text.split(" ")) {
            // Check if the word is a negation term, if so, toggle negation
            if (isNegationWord(word)) {
                negate = !negate;
                continue;
            }

            // Retrieve sentiment scores for the word if it exists in SentiWordNet
            Double[] scores = getWordScores(word);
            if (scores != null) {
                // Reverse the score if negate flag is set
                posTotal += negate ? scores[1] : scores[0];
                negTotal += negate ? scores[0] : scores[1];
                wordCount++;
            }
        }

        if (wordCount == 0) return "neutral"; // Default to neutral if no sentiment-bearing words are found

        double posAvg = posTotal / wordCount;
        double negAvg = negTotal / wordCount;
        double threshold = 0.1;  // Further lowered threshold for finer sentiment separation

        // Classify based on adjusted threshold
        return posAvg > negAvg + threshold ? "positive" : negAvg > posAvg + threshold ? "negative" : "neutral";
    }

    // Helper method to check if a word is a negation term
    private static boolean isNegationWord(String word) {
        return word.equals("not") || word.equals("no") || word.equals("never");
    }

    // Retrieve scores for a word, considering various POS tags
    private static Double[] getWordScores(String word) {
        String[] posTags = {"#n", "#a", "#v"}; // nouns, adjectives, verbs
        for (String pos : posTags) {
            Double[] scores = sentiWordNetMap.get(word + pos);
            if (scores != null) {
                return scores;
            }
        }
        return null;
    }
}
