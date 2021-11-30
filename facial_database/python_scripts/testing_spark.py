import findspark
# findspark.find()

import os
SUBMIT_ARGS = "--packages mysql:mysql-connector-java:8.0.11 pyspark-shell" 
os.environ["PYSPARK_SUBMIT_ARGS"] = SUBMIT_ARGS 
findspark.add_packages('mysql:mysql-connector-java:8.0.11')
findspark.init()

from pyspark.sql import SparkSession
spark = (
    SparkSession.builder
    .appName("pyspark-intro")
    .config("spark.driver.memory", "512m")
    .config("spark.driver.cores", "1")
    .config("spark.executor.memory", "512m")
    .config("spark.executor.cores", "1")
    .config("spark.sql.shuffle.partitions", "2")
    .getOrCreate()
)


df = spark.read.format("jdbc")\
    .option("url", "jdbc:mysql://mysql:3306/facial_db") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("dbtable", "testing_table") \
    .option("user", "WIOS_User") \
    .option("password", "Whoisonscreen!")\
    .load()

print(df.show())

spark.stop()