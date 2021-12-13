import sys
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

##########################
# You can configure master here if you do not pass the spark.master paramenter in conf
##########################
master = "spark://spark:7077"
app_name = "Spark Hello World"
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

# Create spark context
# sc = SparkContext()
sc = spark.sparkContext
sc.setLogLevel("WARN")

# Get the second argument passed to spark-submit (the first is the python app)
logFile = sys.argv[1]

# Read file
logData = sc.textFile(logFile).cache()

# Get lines with A
numAs = logData.filter(lambda s: 'a' in s).count()

# Get lines with B 
numBs = logData.filter(lambda s: 'b' in s).count()

# Print result
print("Lines with a: {}, lines with b: {}".format(numAs, numBs))
