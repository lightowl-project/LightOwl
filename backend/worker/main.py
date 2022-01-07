# from .tasks import parseMessage, executeRule
from config import settings
from celery import Celery


redis_url: str = f"redis://{settings.REDIS_URL}:{settings.REDIS_PORT}"

broker_url: str = f"pyamqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_URL}:{settings.RABBITMQ_PORT}/"
backend_url: str = redis_url

celery = Celery("lightowl", broker=broker_url)

celery.conf.task_routes = {}

# celery.register_task(parseMessage)
# celery.register_task(executeRule)


# celery.steps['consumer'].add(AMQPRetryConsumerStep)
