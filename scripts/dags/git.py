#!/usr/bin/env python
import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=30)
}

dag = DAG('git', default_args=default_args, schedule_interval=None, concurrency=1, max_active_runs=1, catchup=False)

checkout = BashOperator(
    task_id='checkout',
    bash_command='git checkout',
    dag=dag)

if __name__ == "__main__":
    dag.cli()
