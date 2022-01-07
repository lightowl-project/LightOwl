from config import settings
from celery import Celery

redis_url: str = f"redis://{settings.REDIS_URL}:{settings.REDIS_PORT}"

broker_url: str = f"pyamqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_URL}:{settings.RABBITMQ_PORT}/"
backend_url: str = redis_url

app = Celery("lightowl", broker=broker_url)

app.conf.task_routes = {}
app.conf["imports"] = settings.CELERY_IMPORTS

app.autodiscover_tasks()