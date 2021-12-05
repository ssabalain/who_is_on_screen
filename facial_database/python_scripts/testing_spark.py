import findspark
# findspark.find()

import os
SUBMIT_ARGS = "--packages mysql:mysql-connector-java:8.0.11 pyspark-shell" 
os.environ["PYSPARK_SUBMIT_ARGS"] = SUBMIT_ARGS 
findspark.add_packages('mysql:mysql-connector-java:8.0.11')
findspark.init()

from pyspark.sql import SparkSession

def main():
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

    print("reading dataset")
    df = spark.read.format("jdbc")\
        .option("url", "jdbc:mysql://mysql:3306/facial_db") \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .option("dbtable", "imdb_crew_by_title") \
        .option("user", "WIOS_User") \
        .option("password", "Whoisonscreen!")\
        .option("useSSL","false")\
        .load()

    # df.write.parquet("crewbytitle.parquet",mode="overwrite")

    print(df.count())

    spark.stop()

#Counting rows results:
#imdb_crew_by_title 23s
#imdb_actors_by_title 

#Saving into parquet:
#imdb_crew_by_title 34s