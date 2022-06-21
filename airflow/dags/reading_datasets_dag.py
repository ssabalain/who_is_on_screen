from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.python_operator import PythonOperator
from airflow import settings
from airflow.models import Connection
from datetime import datetime, timedelta


###############################################
# Parameters
###############################################

#General
now = datetime.now()
connection_name = "spark_connection"
host_name = "spark://spark"
port_number = 7077
spark_master = host_name + ":" + str(port_number) #"spark://spark:7077"

#Spark Operator
spark_task_id = "spark_job"
spark_script_folder = "/usr/local/spark/app/"
spark_app = "reading_datasets.py"
spark_application_path = spark_script_folder + spark_app # Spark application path created in airflow and spark cluster
#spark_app_name = "Read IMDB Datasets"

#file_path = "/usr/local/spark/resources/data/airflow.cfg"


###############################################
# Functions
###############################################

def creating_conn():
    conn = Connection(
        conn_id = connection_name,
        host= host_name,
        port= port_number,
        extra= '{"queue": "root.default"}'
    )
    session = settings.Session()

    conn_name = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()

    if str(conn_name) == str(connection_name):
        print("Connection " + connection_name + " already exists")
        return

    print("Adding connection...")
    session.add(conn)
    session.commit()
    print("Connection succesfully added...")

###############################################
# DAG Definition
###############################################

id_dag = "reading_imdb_datasets_DAG"
dag_description = "This DAG runs a simple Pyspark app."
default_args = {
    "owner": "ssabalain",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["ssabalain@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

with DAG(
    dag_id= id_dag, 
    description= dag_description,
    default_args=default_args, 
    schedule_interval=timedelta(1)
) as dag:
    dummy_start_task = DummyOperator(
        task_id="start"
    )
    create_connection = PythonOperator(
        task_id='create_connection_airflow',
        python_callable=creating_conn
    )
    spark_job = SparkSubmitOperator(
        task_id= spark_task_id,
        application=spark_application_path, # Spark application path created in airflow and spark cluster
        conn_id=connection_name#,
        #application_args=[file_path]
    )
    dummy_end_task = DummyOperator(
        task_id="end"
    )

dummy_start_task >> create_connection >> spark_job >> dummy_end_task