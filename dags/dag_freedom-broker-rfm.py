from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import timedelta, datetime
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import os

TEAM_SCHEMA = 'schema_twenty'  

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

# Load SQL 
def load_sql(filename):
    """
    Load a SQL file from dags/sql/ given just the filename.
    """
    base_path = os.path.join(os.path.dirname(__file__), 'sql')
    sql_path = os.path.join(base_path, filename)
    print(f"Loading SQL file from: {sql_path}")
    
    with open(sql_path, 'r') as file:
        sql_content = file.read()
        
    sql_content = sql_content.replace('team_twenty', TEAM_SCHEMA)
    
    return sql_content

# Start DAG
with DAG(
    dag_id="freedom_broker_rfm_segmentation",
    default_args=DEFAULT_ARGS,
    description='RFM Segmentation for Freedom Broker',
    catchup=False,
    schedule=None,
    tags=["SDU", "HACKATHON", "FREEDOM_BROKER", "RFM"],
) as dag:
    
    start_op = EmptyOperator(task_id="start")
    end_op = EmptyOperator(task_id="end")

    # Create unified RFM table with all metrics
    create_rfm_table = PostgresOperator(
        task_id="create_rfm_table",
        postgres_conn_id="freedom_broker",
        sql=load_sql("create_rfm_table.sql"),
    )
    
    # Set task dependencies
    start_op >> create_rfm_table >> end_op

# End DAG