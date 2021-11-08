from ..plugins import Plugin
from . import schema

class Apache(Plugin):
    SCHEMA = schema.Apache
    CONFIG_FILE: str = "./plugins/apache/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
