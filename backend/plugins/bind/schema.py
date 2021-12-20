import base64
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import validators
import ipaddress


class Bind(BaseModel):
    """
    This plugin decodes the JSON or XML statistics provided by BIND 9 nameservers.
    """

    urls: List[str] = Field(
        title="URLs",
        description="List of BIND statistics channel URLs to collect from. Do not include a trailing slash in the URL. Exemple: http://localhost:8053/xml/v3"
    )

    gather_memory_contexts: bool = Field(
        False,
        title="Gather Per Memory Context",
        description="Report per-context memory statistics"
    )
    
    gather_views: bool = Field(
        False,
        title="Gather Per View Statistics",
        description="Report per-view query statistics"
    )

    timeout: int = Field(
        4,
        title="Timeout",
        description="Timeout for http requests made by bind nameserver",
        min=1
    )
    
    class Config:
        url: str = "https://github.com/influxdata/telegraf/tree/master/plugins/inputs/bind"
        color: str = "#70b548"
        with open("./plugins/bind/logo/bind.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "180px"
