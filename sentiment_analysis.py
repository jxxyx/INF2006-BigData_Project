# 2302940 Ng Shu Yi
# This code reads the csv file, filters for negative sentiments, cleans and maps country codes to full country names. 
# Groups the data by country, counts the number of complaints for each country and displays the top 5 countries with the highest complaints.

# Import necessary libraries
import os
os.environ["HADOOP_HOME"] = r"C:\Users\emxma\Documents\Sch\INF2006 Cloud Computing\hadoop-3.0.0"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, lower, lit, create_map
from airport_code import country

def initialize_spark(app_name):
    """Initialize Spark session."""
    spark = SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark

def load_data(spark, data_path):
    """Load the dataset."""
    return spark.read.csv(data_path, sep='\t', header=True, inferSchema=True)

def create_country_map(country_dict):
    """Convert the country dictionary to a Spark map column."""
    return create_map([lit(x) for x in sum(country_dict.items(), ())])

def filter_negative_sentiments(df):
    """Filter negative sentiments and ensure _country is not null."""
    return df.filter(
        (col("airline_sentiment") == "negative") & 
        (col("_country").isNotNull())
    )

def clean_country_column(df):
    """Clean the _country column to remove invalid entries."""
    return df.withColumn("_country", regexp_replace(col("_country"), r"[^a-zA-Z\s]", ""))

def map_country_names(df, country_map_expr):
    """Map _country to full country names using the country dictionary."""
    return df.withColumn("country_full_name", country_map_expr[col("_country")])

def group_and_count_complaints(df):
    """Group by country and count complaints."""
    return df.groupBy("country_full_name").count()

def display_top_countries(df, n=5):
    """Display top n countries with the highest complaints."""
    print(f"Top {n} countries with highest complaints:")
    df.orderBy(col("count").desc()).limit(n).show(truncate=False)

def main():
    # Initialize Spark session
    spark = initialize_spark("AirlineSentimentAnalysis")

    # Load the dataset
    data_path = "Airline-Full-Non-Ag-DFE-Sentiment.tsv"
    df = load_data(spark, data_path)

    # Convert the country dictionary to a Spark map column
    country_map_expr = create_country_map(country)

    # Filter negative sentiments and ensure _country is not null
    complaints_df = filter_negative_sentiments(df)

    # Clean the _country column
    complaints_df = clean_country_column(complaints_df)

    # Map _country to full country names using the country dictionary
    complaints_df = map_country_names(complaints_df, country_map_expr)

    # Cache the filtered DataFrame to improve performance if reused
    complaints_df.cache()

    # Group by country and count complaints
    country_complaints = group_and_count_complaints(complaints_df)

    # Display top 5 countries with the highest complaints
    display_top_countries(country_complaints)

if __name__ == "__main__":
    main()