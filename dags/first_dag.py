from airflow.providers.postgres.operators.postgres import PostgresOperator
from pendulum import datetime as pendulum_datetime, now as pendulum_now
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task
from datetime import timedelta
from airflow import DAG

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum_datetime(2025, 5, 2, tz="Asia/Aqtobe"),
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id=f"first_pg_dag",
    default_args=DEFAULT_ARGS,
    catchup=False,
    schedule="@once",
    tags=["SDU", "TEST", "POSTGRES"],
):
    start_op = EmptyOperator(task_id="start")
    end_op = EmptyOperator(task_id="end")

    query = """
        SELECT 
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)) AS age,
            COUNT(*) AS count,
            sex,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY sex), 2) AS percentage_by_gender
        FROM public.freedom_users
        WHERE is_active = true
        GROUP BY age, sex
        ORDER BY sex, age;
    """

    pg_task = PostgresOperator(
        task_id="pg_task",
        postgres_conn_id="freedom_postgres",
        sql=query,
    )

    start_op >> pg_task >> end_op

# End DAG
