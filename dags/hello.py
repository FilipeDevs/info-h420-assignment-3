from datetime import datetime
from airflow.sdk import dag, task

@dag(schedule=None, start_date=datetime(2026, 1, 1), catchup=False)
def hello():
    @task
    def say_hi():
        print("hi from Airflow")
    say_hi()

hello()
