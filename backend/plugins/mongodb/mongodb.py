from ..plugins import Plugin
from . import schema


class MongoDB(Plugin):
    SCHEMA = schema.MongoDB
    CONFIG_FILE: str = "./plugins/mongodb/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
