from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Define the Python function
def hello_world():
    print("Hello, World!")

# Define the DAG
with DAG(
    dag_id='hello_world_dag_ZZZ',
    default_args={'start_date': datetime(2024, 10, 1)},
    schedule_interval='@daily',  # Runs daily
    tags=[f'team_6'],
    catchup=False
) as dag:

    # Define the task
    hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=hello_world
    )

    hello_task