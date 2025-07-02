import os
import boto3
import uuid
import zipfile
import shutil
from datetime import datetime, timezone
from fastapi import UploadFile, Request
    


s3_client = None

def get_s3_client():
    global s3_client
    if s3_client is not None:
        return s3_client

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )
    return s3_client


async def upload_and_get_s3_url(file : UploadFile, generated_file_name : str):
    s3_client = get_s3_client()
    bucket_name = os.environ["AWS_S3_BUCKET_NAME"]

    key = f"pdf/{generated_file_name}"
    file_content = await file.read()
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=file_content)
    
    return f"s3://{bucket_name}/{key}"


def upload_file_to_s3_by_file_path(file_path):
    s3_client = get_s3_client()

    log_filename = generate_log_filename(file_path)

    s3_client.upload_file(
        Filename = file_path,
        Bucket = os.environ["AWS_S3_BUCKET_NAME"],
        Key = log_filename
    )

def generate_log_filename(file_path):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    unique_id = str(uuid.uuid4())
    filename_without_exstension = get_filename_without_extension(file_path)
    file_extension = get_extension_from_file_path(file_path)

    log_filename = f"{timestamp}_{filename_without_exstension}_{unique_id}{file_extension}"
    return log_filename

def get_filename_without_extension(file_path : str):
    filename = os.path.basename(file_path)
    basename, _ = os.path.splitext(filename)
    return basename

def get_extension_from_file_path(file_path : str):
    _, ext = os.path.splitext(file_path)

    return ext


if __name__ == "__main__":
    test_file_name = "hello.pdf"
    generated_log_file_name = generate_log_filename(test_file_name)

    print(generated_log_file_name)