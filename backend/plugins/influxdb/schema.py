import base64
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import validators
import ipaddress


class InfluxDB(BaseModel):
    """
    The InfluxDB plugin will collect metrics on the given InfluxDB servers. Read our documentation for detailed information about influxdb metrics.
    """

    urls: List[str] = Field(
        title="URLs",
        description="An array of URLs. Ex: http://127.0.0.1:8086/debug/vars"
    )

    username: Optional[str] = Field(
        title="Username",
    )

    password: Optional[str] = Field(
        title="Password",
    )

    timeout: int = Field(
        5,
        title="Request & Header Timeout",
        description="Maximum time to receive response (in second)",
        min=1
    )

    insecure_skip_verify: Optional[bool] = Field(
        False,
        title="Insecure Skip Verify",
        description="Use TLS but skip chain & host verification"
    )
    
    class Config:
        color: str = "#70b548"
        with open("./plugins/influxdb/logo/influxdb.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "300px"
