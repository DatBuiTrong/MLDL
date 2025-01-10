from pyspark.sql import SparkSession

# Create spark session
spark = SparkSession.builder.appName('simple spark df')\
        .config("spark.driver.maxResultSize", "4g")\
        .getOrCreate()

data = [("james", "", 'Smith', 30, "M", 60000),
        ("Michael", "Rose", "", 50, "M", 70000),
        ("Maria", "anne", "jones", 38, "F", 500000)]

columns = ["fn", "mn", "ln", "age", "gender", "salary"]
pysparkDF = spark.createDataFrame(data=data, schema = columns)
pysparkDF.printSchema()

print(f'Number of rows: {pysparkDF.count()}')

pysparkDF.show(truncate=False)