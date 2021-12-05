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
    .config("spark.driver.memory", "2g")
    .config("spark.driver.cores", "1")
    .config("spark.executor.memory", "2g") #This number can't exceed the one declared on each worker on the docker-compose file
    .config("spark.executor.cores", "2")
    .config("spark.sql.shuffle.partitions", "2")
    .getOrCreate()
)

df=spark.read.parquet("crewbytitle.parquet")

print(df.count())