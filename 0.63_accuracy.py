from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, when
from pyspark.sql.types import IntegerType, StringType
import nltk
from nltk.corpus import sentiwordnet as swn
from nltk.tokenize import word_tokenize

# Download required NLTK resources (only once)
nltk.download('sentiwordnet')
nltk.download('wordnet')
nltk.download('punkt')

# Initialize Spark session
spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .getOrCreate()

# Load TSV dataset
df = spark.read.csv("cleaned_combined_output.tsv", sep='\t', header=True, inferSchema=True)

# Filter rows with non-null values in 'airline_sentiment_gold' and 'text'
df = df.filter((col("airline_sentiment_gold").isNotNull()) & (col("text").isNotNull()))

# Map 'airline_sentiment_gold' to numeric values
df = df.withColumn(
    "gold_sentiment",
    when(col("airline_sentiment_gold") == "positive", 1)
    .when(col("airline_sentiment_gold") == "negative", -1)
    .when(col("airline_sentiment_gold") == "neutral", 0)
)

# Define the optimized sentiment analysis function using SentiWordNet
def analyze_sentiment_swn(text):
    from nltk.corpus import sentiwordnet as swn
    from nltk import word_tokenize

    if text is None or text.strip() == '':
        return 0  # Neutral for empty or None text
    
    words = word_tokenize(text.lower())
    pos_score, neg_score, word_count = 0, 0, 0

    # Calculate sentiment scores using all synsets
    for word in words:
        synsets = list(swn.senti_synsets(word))
        if synsets:
            pos_score += sum(syn.pos_score() for syn in synsets) / len(synsets)
            neg_score += sum(syn.neg_score() for syn in synsets) / len(synsets)
            word_count += 1

    # Normalize scores if there are valid words with synsets
    if word_count > 0:
        pos_score /= word_count
        neg_score /= word_count

    # Classify based on scores
    if pos_score > neg_score:
        return 1  # Positive
    elif neg_score > pos_score:
        return -1  # Negative
    else:
        return 0  # Neutral

# Register the sentiment analysis function as a Spark UDF
sentiment_udf = udf(analyze_sentiment_swn, IntegerType())

# Apply the UDF to analyze sentiment
df = df.withColumn("predicted_sentiment", sentiment_udf(col("text")))

# Compare predicted sentiment with 'gold_sentiment'
df = df.withColumn(
    "correct", (col("predicted_sentiment") == col("gold_sentiment")).cast(IntegerType())
)

# Calculate accuracy
accuracy = df.selectExpr("avg(correct) as accuracy").collect()[0]["accuracy"]
print(f"\nAccuracy of sentiment analysis: {accuracy:.2f}")

df = df.withColumn(
    "predicted_sentiment_str",
    when(col("predicted_sentiment") == 1, "positive")
    .when(col("predicted_sentiment") == -1, "negative")
    .when(col("predicted_sentiment") == 0, "neutral")
)

# Save the processed DataFrame to a single TSV file
output_file = "processed_output.tsv"
df.select("text", "airline_sentiment_gold", "predicted_sentiment_str") \
  .coalesce(1) \
  .write.option("header", True) \
  .option("sep", "\t") \
  .mode('overwrite') \
  .csv(output_file)

print(f"\nProcessed data saved to '{output_file}'")


# Stop the Spark session
spark.stop()