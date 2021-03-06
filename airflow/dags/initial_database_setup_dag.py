from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

import sys
sys.path.append('/opt/workspace/facial_database/python_scripts/')

import initial_database_setup as db

###############################################
# Parameters
###############################################

bash_file_path = "/opt/workspace/facial_database/bash_files/update_pip.sh " #VERY IMPORTANT TO ADD A FINAL SPACE AFTER .sh. ALSO, TAKE A LOOK AT THE PERMISSIONS!!!
bash_access = "chmod a+x "

###############################################
# DAG Definition
###############################################

id_dag = "1_0_initial_database_setup"
dag_description = "This DAG runs the whole MySQL database setup process"
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
    python_task = PythonOperator(
        task_id='db_setup',
        python_callable= db.main
    )
    dummy_start_task >> bash_task_permissions >> bash_task >> python_task