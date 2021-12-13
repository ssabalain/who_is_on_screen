import sys
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

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

tsv_file = "/usr/local/facial_database/datasets/imdb_datasets/name.basics.tsv.gz"

print("Reading csv...")
df = spark.read.csv(tsv_file,header= True, sep =r'\t')

print(df.count())

