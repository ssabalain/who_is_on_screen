from pathlib import Path
from datetime import datetime
from airflow.models import DAG
# from airflow.operators.docker_operator import DockerOperator
from airflow.providers.docker.operators.docker import DockerOperator
# from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.dummy_operator import DummyOperator

STORE_DIR = Path(__file__).resolve().parent

dag_args = {'owner': 'Santiago', 'retries': 0, 'start_date': datetime(2021, 10, 10)}
with DAG(   
    "test_run_spark_DAG",
    default_args=dag_args,
    schedule_interval = '@once',
    catchup = False
) as dag:
    dummy_start_task = DummyOperator(
        task_id=f'dummy_start'
    )
    # spark_job = DockerOperator(
    #     task_id='spark_job',
    #     image='arjones/pyspark:2.4.5',
    #     api_version='auto',
    #     auto_remove=True,
    #     environment={'MASTER': "spark://master:7077", 'SPARK_NO_DAEMONIZE': "1",'PYSPARK_PYTHON': "python3", 'SPARK_HOME': "/facial_database/python_scripts"},
    #     volumes=['./facial_database:/facial_database'],
    #     command='python testing_spark.py',
    #     docker_url='unix://var/run/docker.sock',
    #     network_mode='bridge'
    # )
    dummy_start_task #>> spark_job