from ..plugins import Plugin
from . import schema


class Docker(Plugin):
    SCHEMA = schema.Docker
    CONFIG_FILE: str = "./plugins/docker/config.ini"
