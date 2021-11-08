from ..plugins import Plugin
from . import schema

class Ping(Plugin):
    SCHEMA = schema.Ping
    CONFIG_FILE: str = "./plugins/ping/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
