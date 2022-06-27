from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
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
connection_type = "spark"
host_name = "spark://spark"
port_number = 7077
spark_master = host_name + ":" + str(port_number) #"spark://spark:7077"

#Spark Operator
spark_task_id = "spark_job"
spark_script_folder = "/usr/local/spark/app/"
spark_app = "reading_datasets.py"
spark_application_path = spark_script_folder + spark_app # Spark application path created in airflow and spark cluster

###############################################
# Functions
###############################################

def creating_conn():
    conn = Connection(
        conn_id = connection_name,
        conn_type = connection_type,
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

id_dag = "2___reading_imdb_datasets"
dag_description = "This DAG runs a simple Pyspark app."
dag_args = {'owner': 'Santiago', 'retries': 0, 'start_date': datetime(2021, 10, 10)}

with DAG(
    dag_id= id_dag,
    description= dag_description,
    default_args=dag_args,
    schedule_interval= '@once'
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