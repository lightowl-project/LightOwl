from pydantic import BaseModel, Field
from typing import List
import base64


class Fail2ban(BaseModel):
    """Read metrics from Fail2ban"""

    use_sudo: bool = Field(
        False,
        title="Use sudo",
        description="Use sudo to run fail2ban-client"
    )

    class Config:
        url: str = "https://github.com/influxdata/telegraf/tree/master/plugins/inputs/fail2ban"
        color: str = "#ef8383"
        with open("./plugins/fail2ban/logo/fail2ban.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "220px"
