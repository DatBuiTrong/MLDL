# Import the necessary modules
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# print green
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))

# Create a SparkSession
spark = SparkSession.builder \
   .appName("Calculate sum") \
   .getOrCreate()

rdd = spark.sparkContext.parallelize(range(1, 100))

prGreen(f"THE SUM IS HERE: {rdd.sum()}")
# Stop the SparkSession
spark.stop()