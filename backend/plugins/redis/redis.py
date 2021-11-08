from ..plugins import Plugin
from . import schema


class Redis(Plugin):
    SCHEMA = schema.Redis
    CONFIG_FILE: str = "./plugins/redis/config.ini"
