import pyspark
from pyspark.sql import SparkSession
spark=SparkSession.builder.appName("read parquet").getOrCreate()

# parDF=spark.read.parquet("pq_data/people.parquet")
parDF=spark.read.parquet("hdfs://namenode:9000/output/people.parquet")  # how to setup path in hadoop: https://stackoverflow.com/a/35061368/18448121
parDF.printSchema()
parDF.show()