from ..plugins import Plugin
from . import schema


class Elasticsearch(Plugin):
    SCHEMA = schema.Elasticsearch
    CONFIG_FILE: str = "./plugins/elasticsearch/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
