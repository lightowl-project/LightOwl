from ..plugins import Plugin
from . import schema


class Haproxy(Plugin):
    SCHEMA = schema.Haproxy
    CONFIG_FILE: str = "./plugins/haproxy/config.ini"
