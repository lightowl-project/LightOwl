from ..plugins import Plugin
from . import schema

class Bind(Plugin):
    SCHEMA = schema.Bind
    CONFIG_FILE: str = "./plugins/bind/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
