from config import settings
import logging.config
import logging
import pika
import json


logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("celery")



def connect_to_rabbit():
    uri: str = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_URL}:{settings.RABBITMQ_PORT}/"
    connection = pika.BlockingConnection(pika.URLParameters(uri))
    channel = connection.channel()
    channel.queue_declare("alerting", durable=True)
    return channel


def push_message(message: dict):
    channel = connect_to_rabbit()
    channel.basic_publish(
        exchange="lightowl",
        routing_key="alerting",
        body=json.dumps(message)
    )