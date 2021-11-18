from ..plugins import Plugin
from . import schema

class RabbitMQ(Plugin):
    SCHEMA = schema.RabbitMQ
    CONFIG_FILE: str = "./plugins/rabbitmq/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
