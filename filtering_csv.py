import pandas as pd
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import stopwords
import re
import nltk
from pyspark.sql import SparkSession
from sklearn.metrics import confusion_matrix, classification_report

# Download NLTK resources
def download_nltk_resources():
    nltk.download('sentiwordnet')
    nltk.download('wordnet')
    nltk.download('stopwords')

# Initialize stopwords
def load_stopwords():
    return set(stopwords.words('english'))

# Define sentiment analysis function using SentiWordNet
def get_sentiment_sentiwordnet(text, stop_words, threshold=0.3):
    if text is None:
        return 'neutral'
    
    # Preprocess text
    text = re.sub(r'[^a-z\s]', '', text.lower())
    words = [word for word in text.split() if word not in stop_words]
    
    pos_score = 0
    neg_score = 0

    # Calculate sentiment scores
    for word in words:
        synsets = list(swn.senti_synsets(word))
        if synsets:
            pos_score += sum(syn.pos_score() for syn in synsets) / len(synsets)
            neg_score += sum(syn.neg_score() for syn in synsets) / len(synsets)

    # Classification based on threshold
    if pos_score > neg_score + threshold:
        return 'positive'
    elif neg_score > pos_score + threshold:
        return 'negative'
    else:
        return 'neutral'

#filtering the data and making are that the remaining fields are not blank for comparison
def preprocess_and_save_data(input_file, output_file, stop_words):
    df = pd.read_csv(input_file)
    filtered_df = df[df['airline_sentiment_gold'].notna() & (df['airline_sentiment_gold'] != '')]
    filtered_df['predicted_sentiment'] = filtered_df['text'].apply(lambda text: get_sentiment_sentiwordnet(text, stop_words))
    filtered_df.to_csv(output_file, index=False)
    print(f"Preprocessing complete. Data saved to '{output_file}'.")

# Load preprocessed data into Spark for further analysis
def load_and_analyze_data_spark(processed_file):
    # Initialize Spark session
    spark = SparkSession.builder.appName("TwitterSentimentAnalysis").getOrCreate()

    # Load processed data
    df_spark = spark.read.csv(processed_file, header=True, inferSchema=True)
    df_spark = df_spark.filter(df_spark.airline_sentiment_gold.isNotNull() & df_spark.predicted_sentiment.isNotNull())
    
    # Convert to Pandas for classification metrics
    pandas_df = df_spark.select("airline_sentiment_gold", "predicted_sentiment").toPandas()
    
    # Calculate accuracy
    correct_predictions = (pandas_df['predicted_sentiment'] == pandas_df['airline_sentiment_gold']).sum()
    total_predictions = len(pandas_df)
    accuracy = correct_predictions / total_predictions
    print(f"\nAccuracy of Sentiment Analysis: {accuracy:.2f}")

    # Confusion matrix and classification report
    print("\nConfusion Matrix:")
    print(confusion_matrix(pandas_df['airline_sentiment_gold'], pandas_df['predicted_sentiment']))
    print("\nClassification Report:")
    print(classification_report(pandas_df['airline_sentiment_gold'], pandas_df['predicted_sentiment']))

    # Stop Spark session
    spark.stop()

# Main function to run the workflow
def main():
    download_nltk_resources()
    stop_words = load_stopwords()

    input_file = 'dataset/Airline-Full-Non-Ag-DFE-Sentiment.csv'
    processed_file = 'dataset/Airline_Sentiment_Processed.csv'

    # Step 1: Preprocess and save data
    preprocess_and_save_data(input_file, processed_file, stop_words)

    # Step 2: Analyze with Spark
    load_and_analyze_data_spark(processed_file)

# Run main function
if __name__ == "__main__":
    main()
