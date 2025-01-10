from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, to_number
from utils.config import connect_config

# variables:
parquet_files_path = "hdfs://namenode:9000/output/pricing.parquet"

# postgres variables
postgres_url = "jdbc:postgresql://postgres-datamart:5432/homecam_database"
table_name = "pricing"
properties = connect_config(filename="/opt/bitnami/spark/work/config/authorization.ini", section='postgresql')

# print green
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))

spark = SparkSession.builder \
    .appName("ParquetHDFSToPostgres") \
    .getOrCreate()

parquet_data = spark.read.parquet(parquet_files_path)

# Convert below columns to timestamp type
parquet_data = parquet_data.withColumn("purchase_date_time", to_timestamp(col("purchase_date_time")))
parquet_data = parquet_data.withColumn("start_date_time", to_timestamp(col("start_date_time")))
parquet_data = parquet_data.withColumn("end_date_time", to_timestamp(col("end_date_time")))

prGreen(parquet_data.count())
parquet_data.printSchema()
parquet_data.show()

parquet_data.write \
    .mode("append") \
    .jdbc(url=postgres_url, table=table_name, properties=properties)

spark.stop()