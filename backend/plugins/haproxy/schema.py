from pydantic import BaseModel, Field
from typing import List, Optional
import base64


class Haproxy(BaseModel):
    """Read metrics of Haproxy via socket or HTTP stats page"""

    servers: List[str] = Field(
       title="Haproxy Servers",
       description="List of Haproxy Server to gather stats about. Ex: https://127.0.0.1:1936/haproxy?stats"
    )

    auth: bool = Field(
        False,
        title="Basic Authentication",
        description=""
    )

    username: Optional[str] = Field(
        title="Username",
    )

    password: Optional[str] = Field(
        title="Password",
        description=""
    )

    insecure_skip_verify: bool = Field(
        False,
        title="Don't verify SSL Certificate",
        description=""
    )

    class Config:
        color: str = "#ef8383"
        with open("./plugins/haproxy/logo/haproxy.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "220px"
