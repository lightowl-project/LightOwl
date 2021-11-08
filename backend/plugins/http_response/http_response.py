from ..plugins import Plugin
from . import schema

class HTTPResponse(Plugin):
    SCHEMA = schema.HTTPResponse
    CONFIG_FILE: str = "./plugins/http_response/config.ini"

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
