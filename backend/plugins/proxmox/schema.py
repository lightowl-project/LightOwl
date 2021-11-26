import base64
from pydantic import BaseModel, Field, validator
from typing import Optional
import validators
import ipaddress


class Proxmox(BaseModel):
    """
    The proxmox plugin gathers metrics about containers and VMs using the Proxmox API.
    
    Telegraf minimum version: Telegraf 1.16.0
    """

    base_url: str = Field(
        title="Base URL",
        description="API connection configuration. The API token was introduced in Proxmox v6.2. Required permissions for user and token : PVEAuditor role on /. Ex: https://127.0.0.1:8006/api2/json/"
    )

    api_token: str = Field(
        title="API Token",
        description="API connection configuration. The API token was introduced in Proxmox v6.2. Required permissions for user and token : PVEAuditor role on /. In format: user@pam!token_name=<secret_token>"
    )

    node_name: str = Field(
        '',
        title="Node Name",
        description="Node Name, defaults to OS hostname"
    )

    insecure_skip_verify: Optional[bool] = Field(
        False,
        title="Insecure Skip Verify",
        description="Use TLS but skip chain & host verification"
    )

    response_timeout: float = Field(
        5.0,
        title="Response Timeout",
        description="Set response_timeouts",
        min=1.0,
    )

    @validator("base_url")
    def validate_base_url(cls, v):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            if not validators.url(v):
                raise ValueError(f"{v} is not a valid IP Address or Domain")

        return v
    
    class Config:
        url: str = "https://github.com/influxdata/telegraf/tree/master/plugins/inputs/proxmox"
        color: str = "#70b548"
        with open("./plugins/proxmox/logo/proxmox.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "290px"
