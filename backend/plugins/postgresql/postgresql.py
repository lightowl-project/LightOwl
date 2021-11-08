from ..plugins import Plugin
from . import schema


class Postgresql(Plugin):
    SCHEMA = schema.Postgresql
    CONFIG_FILE: str = "./plugins/postgresql/config.ini"
