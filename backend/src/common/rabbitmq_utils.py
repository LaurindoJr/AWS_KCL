import os
import pika
import json
from typing import Optional

# RabbitMQ Config
RABBITMQ_HOST  = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.environ.get("RABBITMQ_QUEUE", "image_processing")
RABBITMQ_USER  = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS  = os.environ.get("RABBITMQ_PASS", "guest")

def enqueue_image(s3_key: str, book_id: Optional[int] = None):
    """
    Publica mensagem no RabbitMQ para o worker processar a imagem.
    """
    payload = {"bucket": os.environ.get("BUCKET_NAME", "books"), "key": s3_key}
    if book_id is not None:
        payload["book_id"] = str(book_id)

    try:
        creds = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        params = pika.ConnectionParameters(RABBITMQ_HOST, credentials=creds)
        with pika.BlockingConnection(params) as conn:
            ch = conn.channel()
            ch.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            ch.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
        print(f"Sent message to RabbitMQ: {payload}")
    except Exception as e:
        print(f"Error publishing to RabbitMQ: {e}")
        # log_audit("RABBITMQ_PUBLISH_ERROR", {"error": str(e), "payload": payload}) # log_audit not available here
