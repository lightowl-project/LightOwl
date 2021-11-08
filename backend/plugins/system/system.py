from ..plugins import Plugin
from . import schema



class System(Plugin):
    SCHEMA = schema.System
    CONFIG_FILE: str = "./plugins/system/config.ini"

    GRAPH: dict = {
        "table": "cpu",
        "field": "load1"
    }

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
