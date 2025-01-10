# BASED ON: https://stackoverflow.com/a/54696655/18448121

# from pyspark.sql.column import Column, _to_java_column
# from pyspark import SparkContext
from pyspark.sql.functions import col, struct, explode
from pyspark.sql.avro.functions import from_avro, to_avro
from pyspark.sql import SparkSession

# print green
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))


spark = SparkSession \
  .builder\
  .appName("avro example")\
  .getOrCreate()

# def from_avro(col, jsonFormatSchema): 
#     sc = SparkContext._active_spark_context 
#     avro = sc._jvm.org.apache.spark.sql.avro
#     f = getattr(getattr(avro, "package$"), "MODULE$").from_avro
#     return Column(f(_to_java_column(col), jsonFormatSchema)) 


# def to_avro(col): 
#     sc = SparkContext._active_spark_context 
#     avro = sc._jvm.org.apache.spark.sql.avro
#     f = getattr(getattr(avro, "package$"), "MODULE$").to_avro
#     return Column(f(_to_java_column(col))) 

avro_type_struct = """
{
  "type": "record",
  "name": "struct",
  "fields": [
    {"name": "col1", "type": "long"},
    {"name": "col2", "type": "string"}
  ]
}"""


df = spark.range(10).select(struct(
    col("id"),
    col("id").cast("string").alias("id2")
).alias("struct"))

prGreen("print schema of struct table with column: id, id2")
df.printSchema()

prGreen("show struct table with column: id, id2")
df.select("struct.*").show()

prGreen("show table that converted to avro (convert all columns: id, id2 and then give the new name: avro)")
avro_struct_df = df.select(to_avro(col("struct")).alias("avro"))
avro_struct_df.show()

prGreen("deserialized table")
deserialized_df = avro_struct_df.select(from_avro("avro", avro_type_struct).alias('deserialized_data'))
deserialized_df.show()


deserialized_df = deserialized_df.select(
    "deserialized_data.*"
)
prGreen("show schema, check if the datatype is the same as before serialized")
deserialized_df.printSchema()

prGreen("show the table after restore columns position")
deserialized_df.show()