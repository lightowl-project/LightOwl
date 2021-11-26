import base64
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import validators
import ipaddress


class Apache(BaseModel):
    """
    The Apache plugin collects server performance information using the mod_status module of the Apache HTTP Server. 
    Typically, the mod_status module is configured to expose a page at the /server-status?auto location of the Apache server. 
    The ExtendedStatus option must be enabled in order to collect all available fields. 
    For information about how to configure your server reference the module documentation.
    """

    urls: List[str] = Field(
        title="URLs",
        description="An array of URLs to gather from, must be directed at the machine readable version of the mod_status page including the auto query string"
    )

    username: Optional[str] = Field(
        title="Username",
        description="Credentials for basic HTTP authentication"
    )

    password: Optional[str] = Field(
        title="Password",
        description="Credentials for basic HTTP authentication"
    )

    response_timeout: float = Field(
        5.0,
        title="Response Timeout",
        description="Maximum time to receive response (in second)",
        min=1.0
    )

    insecure_skip_verify: Optional[bool] = Field(
        False,
        title="Insecure Skip Verify",
        description="Use TLS but skip chain & host verification"
    )

    @validator("urls")
    def validate_urls(cls, v):
        for i in v:
            try:
                ipaddress.ip_address(i)
            except ValueError:
                if not validators.url(i):
                    raise ValueError(f"{i} is not a valid IP Address or URL")

        return v
    
    class Config:
        url: str = "https://github.com/influxdata/telegraf/tree/master/plugins/inputs/apache"
        color: str = "#70b548"
        with open("./plugins/apache/logo/apache.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "180px"
