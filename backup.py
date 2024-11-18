from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, when
from pyspark.sql.types import IntegerType, StringType
import nltk
from nltk.corpus import sentiwordnet as swn, stopwords
from nltk.tokenize import word_tokenize
from sklearn.metrics import confusion_matrix, classification_report

# Pre-download required NLTK resources (only once)
nltk.download('sentiwordnet')
nltk.download('wordnet')
nltk.download('stopwords')
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

# Broadcast stopwords list to all worker nodes
stop_words = set(stopwords.words('english'))
stop_words_broadcast = spark.sparkContext.broadcast(stop_words)

# Define the optimized sentiment analysis function using SentiWordNet
def analyze_sentiment_swn(text):
    from nltk.corpus import sentiwordnet as swn
    from nltk.tokenize import word_tokenize

    stop_words = stop_words_broadcast.value

    if text is None or text.strip() == '':
        return 0  # Neutral for empty or None text

    words = word_tokenize(text.lower())
    words = [word for word in words if word not in stop_words]
    
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

# Calculate accuracy using Spark DataFrame operations
accuracy = df.selectExpr("avg(correct) as accuracy").collect()[0]["accuracy"]
print(f"\nAccuracy of Sentiment Analysis (using Spark DataFrame): {accuracy:.2f}")

# Convert predicted sentiment to string for confusion matrix
df = df.withColumn(
    "predicted_sentiment_str",
    when(col("predicted_sentiment") == 1, "positive")
    .when(col("predicted_sentiment") == -1, "negative")
    .when(col("predicted_sentiment") == 0, "neutral")
)

# Ensure both columns are strings for comparison
df = df.withColumn("gold_sentiment_str", col("airline_sentiment_gold").cast(StringType()))

# Save the processed DataFrame to a new TSV file
output_file = "processed_output.tsv"
df.select("text", "airline_sentiment_gold", "predicted_sentiment_str").write.csv(
    output_file, sep='\t', header=True, mode='overwrite'
)
print(f"\nProcessed data saved to '{output_file}'")

# Convert to Pandas DataFrame for confusion matrix and classification report
pandas_df = df.select("gold_sentiment_str", "predicted_sentiment_str").toPandas()

# Generate confusion matrix and classification report
print("\nConfusion Matrix:")
conf_matrix = confusion_matrix(
    pandas_df['gold_sentiment_str'], 
    pandas_df['predicted_sentiment_str'], 
    labels=['positive', 'negative', 'neutral']
)
print(conf_matrix)

print("\nClassification Report:")
print(classification_report(
    pandas_df['gold_sentiment_str'], 
    pandas_df['predicted_sentiment_str'], 
    labels=['positive', 'negative', 'neutral']
))

# Stop the Spark session
spark.stop()
