from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

import sys
sys.path.append('/opt/workspace/src/python_scripts/')

import setup_director_database as db_setup
import setup_facial_dataset as dataset_setup

###############################################
# Parameters
###############################################

bash_file_path = "/opt/workspace/src/bash_files/update_pip.sh " #VERY IMPORTANT TO ADD A FINAL SPACE AFTER .sh. ALSO, TAKE A LOOK AT THE PERMISSIONS!!!
bash_access = "chmod a+x "

###############################################
# DAG Definition
###############################################

id_dag = "4__facial_dataset_setup"
dag_description = "This DAG creates a MySQL database for a specific director, with all the necessary tables, and then downloads the facial dataset"
dag_args = {
    'owner': 'Santiago',
    'retries': 0,
    'catchup': False,
    'start_date': datetime(2021, 10, 10)
}

with DAG(
    dag_id= id_dag,
    description= dag_description,
    default_args=dag_args,
    schedule_interval= '@once'
) as dag:
    dummy_start_task = DummyOperator(
        task_id=f'dummy_start'
    )
    bash_task_permissions = BashOperator(
        task_id= f'bash_changing_permissions',
        bash_command= bash_access + bash_file_path
    )
    bash_task = BashOperator(
        task_id= f'bash_executing_task',
        bash_command= bash_file_path
    )
    python_task_1 = PythonOperator(
        task_id='database_setup',
        python_callable= db_setup.main
    )
    python_task_2 = PythonOperator(
        task_id='facial_dataset_setup',
        python_callable= dataset_setup.main
    )
    dummy_start_task >> bash_task_permissions >> bash_task >> python_task_1 >> python_task_2