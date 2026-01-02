#!/usr/bin/env python3
import os, json, io, time
from datetime import datetime, timezone
import boto3
import pika
from PIL import Image
from typing import Optional
from botocore.client import Config

# AWS / DynamoDB
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DDB_AUDIT = os.environ.get("DDB_AUDIT", "kcl-AuditLogs")
DDB_STATUS = os.environ.get("DDB_STATUS", "kcl-ProcessingStatus")

# MinIO / S3
MINIO_ENDPOINT_URL = os.environ.get("MINIO_ENDPOINT_URL")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET", "books")
THUMB_PREFIX = os.getenv("THUMB_PREFIX", "thumb/")

# RabbitMQ
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.environ.get("RABBITMQ_QUEUE", "image_processing")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")

# Clients
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=MINIO_ENDPOINT_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
)
ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
status_tb = ddb.Table(DDB_STATUS) if DDB_STATUS else None
audit_tb = ddb.Table(DDB_AUDIT) if DDB_AUDIT else None

# Helper Functions
def now_iso():
    return datetime.now(timezone.utc).isoformat()

def log(msg):
    print(f"[{now_iso()}] {msg}", flush=True)

def update_status(key: str, status: str, info: Optional[dict] = None):
    if not status_tb: return
    try:
        status_tb.update_item(
            Key={"pk": key, "sk": "STATUS"},
            UpdateExpression="SET #s=:s, info=:i, updated_at=:t",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": status, ":i": info or {}, ":t": now_iso()},
        )
    except Exception as e:
        log(f"ERROR: Could not update status for {key}. Reason: {e}")

def log_audit(action: str, data: dict, s3_key: Optional[str] = None):
    if not audit_tb: return
    try:
        item = {
            "pk": f"WORKER#{action}",
            "sk": s3_key if s3_key else str(time.time()),
            "action": action,
            "data": data,
            "at": now_iso(),
        }
        audit_tb.put_item(Item=item)
    except Exception as e:
        log(f"ERROR: Could not log audit action {action}. Reason: {e}")

# Core Logic
def make_thumb(obj_key: str) -> str:
    log(f"Downloading s3://{S3_BUCKET}/{obj_key}")
    obj = s3.get_object(Bucket=S3_BUCKET, Key=obj_key)
    body = obj["Body"].read()
    img = Image.open(io.BytesIO(body))
    img.thumbnail((256, 256))

    buf = io.BytesIO()
    fmt = (img.format or "JPEG").upper()
    if fmt == "PNG":
        img.save(buf, format="PNG", optimize=True)
        out_key = f"{THUMB_PREFIX}{os.path.basename(obj_key).rsplit('.', 1)[0]}.png"
        content_type = "image/png"
    else:
        img.save(buf, format="JPEG", quality=85, optimize=True)
        out_key = f"{THUMB_PREFIX}{os.path.basename(obj_key).rsplit('.', 1)[0]}.jpg"
        content_type = "image/jpeg"

    buf.seek(0)
    log(f"Uploading thumb to s3://{S3_BUCKET}/{out_key}")
    s3.put_object(Bucket=S3_BUCKET, Key=out_key, Body=buf.getvalue(), ContentType=content_type)
    return out_key

def process_message_callback(ch, method, properties, body):
    log(f"Received message: {body.decode()}")
    key = None
    try:
        payload = json.loads(body)
        key = payload.get("key")
        if not key:
            raise ValueError("Message does not contain a 'key'")

        update_status(key, "PROCESSING", {"source": "rabbitmq-worker"})
        
        thumb_key = make_thumb(key)
        
        update_status(key, "DONE", {"thumb_key": thumb_key})
        log_audit("IMAGE_RESIZED", {"key": key, "thumb_key": thumb_key}, s3_key=key)
        log(f"SUCCESS: {key} -> {thumb_key}")

    except Exception as e:
        log(f"ERROR processing message for key '{key}': {e}")
        if key:
            update_status(key, "ERROR", {"error": str(e), "raw_body": body.decode()})
        log_audit("PROCESSING_ERROR", {"error": str(e), "raw_body": body.decode()}, s3_key=key)

    finally:
        log("Acknowledging message.")
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Main Execution
def main():
    log("Worker starting. Connecting to RabbitMQ...")
    connection = None
    while True:
        try:
            creds = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            params = pika.ConnectionParameters(RABBITMQ_HOST, credentials=creds)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=process_message_callback)

            log(f"Connected to RabbitMQ. Waiting for messages in queue '{RABBITMQ_QUEUE}'.")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            log(f"Connection to RabbitMQ failed: {e}. Retrying in 5 seconds...")
            if connection and not connection.is_closed:
                connection.close()
            time.sleep(5)
        except Exception as e:
            log(f"An unexpected error occurred: {e}. Restarting consumer...")
            if connection and not connection.is_closed:
                connection.close()
            time.sleep(10)

if __name__ == "__main__":
    main()