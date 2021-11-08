from pydantic import BaseSettings
from dotenv import load_dotenv
import random
import string
import os

load_dotenv()


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string


try:
    from secret_key import SECRET_KEY
except ImportError:
    secret_key: str = get_random_string(64)
    with open("./secret_key.py", "w") as f:
        f.write(f"SECRET_KEY: str = '{secret_key}'")

    from secret_key import SECRET_KEY

class AppSettings(BaseSettings):
    DEBUG: bool = os.environ.get("debug")
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CA_PATH: str = "/etc/ssl/lightowl/ca.pem"
    SECRET_KEY: str = SECRET_KEY


class RedisSettings(BaseSettings):
    REDIS_URL: str = os.environ.get("redis_url")
    REDIS_PORT: int = os.environ.get("redis_port")


class RabbitMQSettings(BaseSettings):
    RABBITMQ_URL: str = os.environ.get("rabbitmq_url")
    RABBITMQ_PORT: int = os.environ.get("rabbitmq_port")
    RABBITMQ_USER: str = os.environ.get("rabbitmq_user")
    RABBITMQ_PASSWORD: str = os.environ.get("rabbitmq_password")


class DatabaseSettings(BaseSettings):
    MONGO_URL: str = os.environ.get("mongodb_url")
    MONGO_DATABASE: str = os.environ.get("mongodb_database")
    MONGO_USER: str = os.environ.get('mongodb_user')
    MONGO_PASSWORD: str = os.environ.get("mongodb_password")
    MONGO_AUTHSOURCE: str = os.environ.get("mongodb_authsource")


class InfluxSettings(BaseSettings):
    INFLUX_URL: str = os.environ.get("influx_url")
    INFLUX_PORT: int = os.environ.get("influx_port", 8086)
    INFLUX_DATABASE: str = os.environ.get("influx_database")


class LogSettings(BaseSettings):
    LOG_LEVEL: str = os.environ.get("log_level", "INFO")
    LOG_FILE: str = "/var/log/lightowl/supervision.log"
    LOGGING_FORMAT = '{"date": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "module":"%(module)s", "line_number": %(lineno)s, "message": "%(message)s"}'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            "verbose": {
                "format": LOGGING_FORMAT,
                "datefmt": "%Y-%m-%dT%H:%M:%S%z"
            },
            "simple": {
                "format": "[%(levelname)s] [<%(name)s>:%(module)s:%(lineno)s] "
                        "%(message)s"
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'debug': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': LOG_FILE,
                'formatter': 'verbose'
            },
            'api': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': LOG_FILE,
                'formatter': 'verbose'
            },
            'celery': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': LOG_FILE,
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'debug': {
                'handlers': ['debug'],
                'level': LOG_LEVEL
            },
            'api': {
                'handlers': ['api'],
                'level': LOG_LEVEL
            },
            'celery': {
                'handlers': ['celery'],
                'level': LOG_LEVEL
            },
        }
    }

class Settings(
    AppSettings,
    DatabaseSettings,
    RedisSettings,
    RabbitMQSettings,
    InfluxSettings,
    LogSettings
):
    pass

settings = Settings()

