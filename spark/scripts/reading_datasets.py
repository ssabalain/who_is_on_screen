import sys
import time
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

#Initializing Spark Session
master = "spark://spark:7077"
app_name = "Reading dataset with Spark"
spark = (
    SparkSession.builder
    .appName(app_name)
    .master(master)
    .config("spark.driver.memory", "512m")
    .config("spark.driver.cores", "1")
    .config("spark.executor.memory", "2g")
    .config("spark.executor.cores", "2")
    .config("spark.sql.shuffle.partitions", "2")
    .getOrCreate()
)
sc = spark.sparkContext
sc.setLogLevel("WARN")

print("Spark version: " + str(spark.version))

#Reading tsv.gz file
datasets_path = "/usr/local/facial_database/datasets/imdb_datasets/"
tsv_file = "name.basics.tsv.gz"

print("Reading csv...")
starttime = time.time()
df = spark.read.csv(datasets_path + tsv_file,header= True, sep =r'\t')
endtime = time.time()
exec_time = str(endtime - starttime)

print(f"File {tsv_file} succesfully read and loaded as a Spark dataframe in {exec_time} seconds.")
print(f"Counting the amount of records in {tsv_file}")

starttime = time.time()
total_records = df.count()
endtime = time.time()
exec_time = str(endtime - starttime)

print(f"Counting finished in {exec_time} seconds. Total amount of records is {total_records}. ")