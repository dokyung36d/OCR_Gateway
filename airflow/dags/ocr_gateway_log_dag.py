from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email
from airflow.utils.dates import days_ago
from airflow.exceptions import AirflowFailException

import boto3
import pandas as pd
import os
import json
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from api.aws import get_s3_client


LOCAL_LOG_DIR = os.environ["LOCAL_LOG_DIR"]
AWS_LOG_DIR = os.environ["AWS_S3_LOG_DIR"]
AWS_S3_BUCKET_NAME = os.environ["AWS_S3_BUCKET_NAME"]


default_args = {
    'owner': 'airflow',
    'email_on_failure': False,
}

dag = DAG(
    dag_id='ocr_logging_analysis_dag',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False
)


def upload_files_to_s3():
    s3 = get_s3_client()
    failed = []

    for filename in os.listdir(LOCAL_LOG_DIR):
        if filename.endswith('.json'):
            path = os.path.join(LOCAL_LOG_DIR, filename)
            key = f"log/{filename}"
            try:
                with open(path, 'rb') as f:
                    s3.put_object(Bucket=AWS_S3_BUCKET_NAME, Key=key, Body=f)
            except Exception as e:
                failed.append(filename)
    if failed:
        raise AirflowFailException(f"Upload failed for: {failed}")

def delete_local_logs():
    for filename in os.listdir(LOCAL_LOG_DIR):
        if filename.endswith('.json'):
            os.remove(os.path.join(LOCAL_LOG_DIR, filename))

def send_failure_email(context):
    subject = "[Airflow] Task Failed"
    body = f"Task {context['task_instance'].task_id} failed.\nException: {context.get('exception')}"
    send_email(
        to=["dokyung36d@gmail.com"],  # 실제 받을 이메일로 수정
        subject=subject,
        html_content=body
    )


# DAG Task 정의
upload_task = PythonOperator(
    task_id='upload_files_to_s3',
    python_callable=upload_files_to_s3,
    on_failure_callback=send_failure_email,
    dag=dag
)

delete_task = PythonOperator(
    task_id='delete_local_logs',
    python_callable=delete_local_logs,
    dag=dag
)

upload_task >> delete_task


if __name__ == "__main__":
    upload_files_to_s3()