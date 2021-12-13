from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

import sys
sys.path.append('/usr/local/facial_database/python_scripts/')

import initial_database_setup as db

bash_file_path = "/usr/local/facial_database/bash_files/update_pip.sh " #VERY IMPORTANT TO ADD A FINAL SPACE AFTER .sh. ALSO, TAKE A LOOK AT THE PERMISSIONS!!!
bash_access = "chmod a+x "


now = datetime.now()
dag_args = {
    "owner": "Santiago",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

with DAG(   
    "download_imdb_datasets_DAG",
    default_args=dag_args,
    schedule_interval = timedelta(1)
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
        task_id='download_datasets',
        python_callable= db.download_datasets
    )
    dummy_start_task >> bash_task_permissions >> bash_task >> python_task