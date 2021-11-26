# packages_required = ["airflow"]

# for packs in packages_required:
#    cp.check_package(packs)

from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

import sys
sys.path.append('/usr/local/python_scripts/')

import check_packages as cp


bash_file_path = "/usr/local/bash_files/my_testing_bash.sh " #VERY IMPORTANT TO ADD A FINAL SPACE AFTER .sh. ALSO, TAKE A LOOK AT THE PERMISSIONS!!!
bash_access = "chmod a+x "

dag_args = {'owner': 'Santiago', 'retries': 0, 'start_date': datetime(2021, 10, 10)}

with DAG(   
    "my_testing_DAG",
    default_args=dag_args,
    schedule_interval = '@once',
    catchup = False
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
    dummy_start_task >> bash_task_permissions >>  bash_task