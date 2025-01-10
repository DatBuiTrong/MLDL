# Import the necessary modules
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# print green
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))

# Create a SparkSession
spark = SparkSession.builder \
   .appName("Read csv") \
   .getOrCreate()

brewfile = spark.read.csv("hdfs://namenode:9000/data/openbeer/breweries/breweries.csv")
  
brewfile.show()