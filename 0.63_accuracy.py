from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
import pandas as pd
import nltk
from nltk.corpus import sentiwordnet as swn
from nltk.tokenize import word_tokenize

# Download required NLTK resources
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

# Convert Spark DataFrame to Pandas DataFrame
pandas_df = df.select("text", "airline_sentiment_gold", "gold_sentiment").toPandas()

# Define sentiment analysis function
def analyze_sentiment(text):
    if text is None or text.strip() == '':
        return 0  # Neutral for empty or None text

    words = word_tokenize(text.lower())
    pos_score, neg_score, word_count = 0, 0, 0

    for word in words:
        synsets = list(swn.senti_synsets(word))
        if synsets:
            pos_score += sum(syn.pos_score() for syn in synsets) / len(synsets)
            neg_score += sum(syn.neg_score() for syn in synsets) / len(synsets)
            word_count += 1

    if word_count > 0:
        pos_score /= word_count
        neg_score /= word_count

    if pos_score > neg_score:
        return 1  # Positive
    elif neg_score > pos_score:
        return -1  # Negative
    else:
        return 0  # Neutral

# Apply sentiment analysis function to Pandas DataFrame
pandas_df["predicted_sentiment"] = pandas_df["text"].apply(analyze_sentiment)

# Map numeric predicted sentiment back to string values
def map_sentiment_label(value):
    if value == 1:
        return "positive"
    elif value == -1:
        return "negative"
    else:
        return "neutral"

pandas_df["predicted_sentiment_str"] = pandas_df["predicted_sentiment"].apply(map_sentiment_label)

# Add a column for correctness
pandas_df["correct"] = (pandas_df["predicted_sentiment"] == pandas_df["gold_sentiment"]).astype(int)

# Convert back to Spark DataFrame
final_df = spark.createDataFrame(pandas_df)

# Save the processed DataFrame to a single TSV file
output_file = "processed_output"
final_df.coalesce(1).select(
    col("text").alias("Text"),
    col("airline_sentiment_gold").alias("Actual Sentiment"),
    col("predicted_sentiment_str").alias("Predicted Sentiment"),
    col("correct").alias("Correct (1=True, 0=False)")
).write.option("header", True) \
    .option("sep", "\t") \
    .mode('overwrite') \
    .csv(output_file)

print(f"\nProcessed data saved to '{output_file}' as a single TSV file.")

# Stop the Spark session
spark.stop()
