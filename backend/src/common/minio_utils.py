import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from typing import Optional, Iterable

# MinIO Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MINIO_ENDPOINT_URL = os.environ.get("MINIO_ENDPOINT_URL")
MINIO_PUBLIC_URL = os.environ.get("MINIO_PUBLIC_URL")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "books")

minio_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=MINIO_ENDPOINT_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4'),
)

def init_minio_bucket():
    """
    Creates the MinIO bucket if it doesn't exist.
    """
    try:
        minio_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' já existe.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Bucket '{BUCKET_NAME}' não existe. Criando...")
            minio_client.create_bucket(Bucket=BUCKET_NAME)
            print(f"Bucket '{BUCKET_NAME}' criado.")
        else:
            print("Erro ao verificar o bucket:")
            raise

def generate_presigned_url(key: str, minutes: int = 60) -> str:
    """
    Generates a presigned URL for an object in MinIO.
    """
    minio_path_style_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        endpoint_url=MINIO_PUBLIC_URL,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
    )
    return minio_path_style_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": key},
        ExpiresIn=minutes * 60,
    )

def upload_file(file, key: str):
    """
    Uploads a file-like object to MinIO.
    """
    try:
        minio_client.upload_fileobj(file, BUCKET_NAME, key, ExtraArgs={"ContentType": file.mimetype})
    except ClientError as e:
        # You might want to log this error
        raise e

def check_object_exists(key: str) -> bool:
    """
    Checks if an object exists in MinIO.
    """
    try:
        minio_client.head_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise e

def thumb_candidate_keys(image_key: Optional[str]):
    """
    Generates potential thumbnail keys for a given image key.
    """
    if not image_key:
        return []
    base_name = os.path.basename(image_key).rsplit('.', 1)[0]
    return [
        f"thumb/{base_name}.png",
        f"thumb/{base_name}.jpg",
    ]

def delete_object(key: str) -> bool:
    """
    Deletes an object in MinIO. Returns True if deleted (or didn't exist), False only in rare cases.
    """
    if not key:
        return True
    try:
        minio_client.delete_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except ClientError as e:
        Exception(f"Failed deleting object: {e}")
        raise e


def delete_objects(keys: Iterable[str]) -> None:
    """
    Deletes multiple objects in MinIO (best effort).
    """
    keys = [k for k in keys if k]
    if not keys:
        return

    for i in range(0, len(keys), 1000):
        batch = keys[i:i+1000]
        resp = minio_client.delete_objects(
            Bucket=BUCKET_NAME,
            Delete={"Objects": [{"Key": k} for k in batch], "Quiet": True},
        )
        errs = resp.get("Errors", [])
        if errs:
            Exception(f"Failed deleting objects: {errs}")
            pass
