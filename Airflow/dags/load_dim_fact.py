import os
import json
from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
# from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago
from resources.bigquery.sql_queries import SqlQueries


# Path to the JSON configuration file
config_file_path = os.path.join(os.path.dirname(__file__), 'config/development.json')

# Read the JSON configuration file
with open(config_file_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

project_id = config['project_id']
dataset_id = config['dataset_id']
team_id = config['team_id']

dim_customer_id = "dim_customer"
dim_product_id = "dim_product"
dim_city_id = "dim_city"
fact_transaction_id = "fact_transaction"

table_customer_raw_id = "raw_customer"
table_product_raw_id = "raw_master_product"
table_city_raw_id = "raw_master_city"
table_transaction_raw_id = "raw_transaction"

dim_customer_insert = SqlQueries.dim_customer_insert.format(
                        project_id=project_id,
                        dataset_id=dataset_id,
                        dim_customer_id=dim_customer_id,
                        table_customer_raw_id = table_customer_raw_id
                    )
dim_product_insert = SqlQueries.dim_product_insert.format(
                        project_id=project_id,
                        dataset_id=dataset_id,
                        dim_product_id=dim_product_id,
                        table_product_raw_id = table_product_raw_id
                    )
dim_city_insert = SqlQueries.dim_city_insert.format(
                        project_id=project_id,
                        dataset_id=dataset_id,
                        dim_city_id=dim_city_id,
                        table_city_raw_id = table_city_raw_id
                    )
fact_transaction_insert = SqlQueries.fact_transaction_insert.format(
                        project_id=project_id,
                        dataset_id=dataset_id,
                        fact_transaction_id=fact_transaction_id,
                        dim_customer_id=dim_customer_id,
                        dim_product_id=dim_product_id,
                        table_transaction_raw_id = table_transaction_raw_id
                    )

# Define default arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 1),
    'retries': 1,
}

# Define the DAG
with DAG(
    dag_id=f'load_dim_fact_{team_id}',
    default_args=default_args,
    description='A DAG to load data from BigQuery to dim fact table',
    schedule_interval='@daily',  # Runs daily
    tags=[f'team_{team_id}']
) as dag:

    # Define the BigQuery task to create a new table
    load_dim_customer = BigQueryInsertJobOperator(
        task_id='load_dim_customer',
        configuration={
            "query": {
                "query": dim_customer_insert,
                "useLegacySql": False,
            }
        }
    )

    load_dim_product = BigQueryInsertJobOperator(
        task_id='load_dim_product',
        configuration={
            "query": {
                "query": dim_product_insert,
                "useLegacySql": False,
            }
        }
    )

    load_dim_city = BigQueryInsertJobOperator(
        task_id='load_dim_city',
        configuration={
            "query": {
                "query": dim_product_insert,
                "useLegacySql": False,
            }
        }
    )

    load_fact_transaction = BigQueryInsertJobOperator(
        task_id='load_fact_transaction',
        configuration={
            "query": {
                "query": fact_transaction_insert,
                "useLegacySql": False,
            }
        }
    )

    # Set task dependencies
    [load_dim_customer, load_dim_product, load_dim_city] >> load_fact_transaction
