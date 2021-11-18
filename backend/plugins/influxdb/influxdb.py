from ..plugins import Plugin
from . import schema

class InfluxDB(Plugin):
    SCHEMA = schema.InfluxDB
    CONFIG_FILE: str = "./plugins/influxdb/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
