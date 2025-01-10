from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import * 

def workwithdf(spark):
  # Loading DataFrames: CSV method 1 using spark.read.csv('path')
  csv_path = 'hdfs://namenode:9000/player.csv'
  player_df =spark.read.option('header', True).option('inferSchema', True).csv(csv_path)

  
  # Selecting multiple columns
  df = player_df.select('player_api_id')
  df.show(5,False)

  
  
#   # Add and update columns # notes Spark withColumn() is a DataFrame function that is used to add a new column to DataFrame, change the value of an existing column, convert the datatype of a column, derive a new column from an existing column
  
#   player_df = player_df.withColumn("country", lit("USA"))
#   player_df = player_df.withColumn("height", col('height')/2.54)
  
#   # Rename columns #notes Spark has a withColumnRenamed() function on DataFrame to change a column name. This is the most straight forward approach; this function takes two parameters; the first is your existing column name and the second is the new column name you wish for.
#   player_df.withColumnRenamed('height', 'height_in_cms')
  
#   # Drop columns 
  
#   player_df = player_df.drop('id', 'player_fifa_api_id')
#   player_df.columns
  
#   player_attr_df = player_attr_df.drop(
#     'id', 
#     'player_fifa_api_id', 
#     'preferred_foot',
#     'attacking_work_rate',
#     'defensive_work_rate',
#     'crossing',
#     'jumping',
#     'sprint_speed',
#     'balance',
#     'aggression',
#     'short_passing',
#     'potential'
#    )
#   player_attr_df.columns
  
#   # When and otherwise 
#   player_df = player_df.withColumn("region", when(col("country") == "USA","North America").otherwise("Unknown"))
  
#   # Where and Filter
  
#   # Distinct
  
#   player_attr_df.select('player_api_id')\
#                    .distinct()\
#                    .count()
  
#   # Sort
 
#   player_df = player_df.orderBy('player_api_id')
#   player_df.show(5, False)
  
#   # Aggregation
  
#   player_attr_df = player_attr_df.groupBy('player_api_id')\
#                        .agg({
#                            'finishing':"avg",
#                            "shot_power":"avg",
#                            "acceleration":"avg"
#                        })
  
#   # join
  
#   join_df = player_df.join( player_attr_df, player_df.player_api_id == player_attr_df.player_api_id , 'inner')
 
  
#   # partitioning 
#   # No.1 repartition() & coalesce()
#   # No. 2 partitionBy()
#   join_df = join_df.repartition(4)
  
#   '''df.write.option("header",True) \
#             .partitionBy("year") \
#             .mode("overwrite") \
#             .csv("/tmp/zipcodes-state")
#    '''
 
if __name__ == "__main__":
  spark = SparkSession \
    .builder \
    .appName("Analyzing soccer players1") \
    .getOrCreate()
  
  workwithdf(spark)
  
  spark.stop()