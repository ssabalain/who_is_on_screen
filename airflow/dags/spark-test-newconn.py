from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.python_operator import PythonOperator


from airflow import settings
from airflow.models import Connection

from datetime import datetime, timedelta

def creating_conn():
    conn = Connection(
        conn_id = "testing_conn_3",
        host= "spark://spark",
        port= 7077,
        extra= '{"queue": "root.default"}'
    )

    session = settings.Session()
    session.add(conn)
    session.commit()

###############################################
# Parameters
###############################################
spark_master = "spark://spark:7077"
spark_app_name = "Spark Hello World _ New Conn"
file_path = "/usr/local/spark/resources/data/airflow.cfg"

###############################################
# DAG Definition
###############################################
now = datetime.now()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

dag = DAG(
        dag_id="spark-test-newConn", 
        description="This DAG runs a simple Pyspark app.",
        default_args=default_args, 
        schedule_interval=timedelta(1)
    )

start = DummyOperator(task_id="start", dag=dag)

create_connection = PythonOperator(
    task_id='create_connection_airflow',
    python_callable=creating_conn,
    dag=dag
)

spark_job = SparkSubmitOperator(
    task_id="spark_job",
    application="/usr/local/spark/app/hello-world.py", # Spark application path created in airflow and spark cluster
    name=spark_app_name,
    conn_id="testing_conn_3",
    verbose=1,
    conf={"spark.master":spark_master},
    application_args=[file_path],
    dag=dag)

end = DummyOperator(task_id="end", dag=dag)

start >> create_connection >> spark_job >> end