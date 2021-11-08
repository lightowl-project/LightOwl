from ..plugins import Plugin
from . import schema


class Fail2ban(Plugin):
    SCHEMA = schema.Fail2ban
    CONFIG_FILE: str = "./plugins/fail2ban/config.ini"
