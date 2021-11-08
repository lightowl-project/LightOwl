from ..plugins import Plugin
from . import schema

class Proxmox(Plugin):
    SCHEMA = schema.Proxmox
    CONFIG_FILE: str = "./plugins/proxmox/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
