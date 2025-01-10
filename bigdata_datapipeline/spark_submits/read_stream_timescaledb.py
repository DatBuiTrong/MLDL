import os
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.column import Column, _to_java_column 

from pyspark.sql.functions import col, from_json, explode, count
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.types import DataType, StructType
import requests
import json

# variables
topic = "timescaledb.data.pricing"
schemaregistry = "http://schema-registry:8081"
kafka_brokers = "kafka-0:9092,kafka-1:9092,kafka-2:9092"
hdfs_path = "hdfs://namenode:9000/output"

# get schema-registry
response = requests.get(f'{schemaregistry}/subjects/{topic}-value/versions/latest/schema')

# error check
response.raise_for_status()

# extract the schema from the response
schema = response.text

# create spark session
spark = SparkSession \
  .builder\
  .appName("read kafka")\
  .getOrCreate()

# https://spark.apache.org/docs/2.2.0/structured-streaming-kafka-integration.html#creating-a-kafka-source-for-batch-queries
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_brokers) \
  .option("subscribe", topic) \
  .option("startingOffsets", "earliest")  \
  .option("includeHeaders", "true") \
  .load()

# print out kafka information
df = df.selectExpr("CAST(topic AS STRING)", "CAST(partition AS STRING)", "CAST(offset AS STRING)", "CAST(key AS STRING)", "substring(value, 6) as avro_value")  # Skip the first 5 bytes (reserved by schema registry encoding protocol)
df = df.select(col('topic'), col('partition'), col('offset'), col('key'), from_avro('avro_value', schema).alias('deserialized_value'))

# Convert bach to original columns like input schema
df = df.select("deserialized_value.*")
df = df.select("after.*") # select the specific column and expand it
df.printSchema()

def process_batch(df, epoch_id, hdfs_path):
    # Print row count and DataFrame
    print(f"Batch: {epoch_id}, Row Count: {df.count()}\n{df.show()}")
    print(df.show())

    # Write to HDFS in Parquet format
    df.write.parquet(f"{hdfs_path}/pricing.parquet", mode="append")

# write to console
query = df.writeStream \
    .format("console") \
    .option("truncate", True) \
    .foreachBatch(lambda df, epoch_id: process_batch(df, epoch_id, hdfs_path)) \
    .option("checkpointLocation", f"{hdfs_path}/checkpoint_pricing") \
    .start()
query.awaitTermination()
spark.stop()