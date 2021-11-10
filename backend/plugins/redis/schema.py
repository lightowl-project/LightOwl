from pydantic import BaseModel, Field
from typing import List
import base64


class Redis(BaseModel):
    """Collect Redis's basic status information"""

    urls: List[str] = Field(
        title="URLs",
        description="List of Redis URL. Example: tcp://localhost:6379"
    )

    password: str = Field(
        "",
        title="Server Password",
        advanced=True
    )

    class Config:
        color: str = "#ef8383"
        with open("./plugins/redis/logo/redis.png", 'rb') as f:
            logo = f.read()

        img = base64.b64encode(logo)
        img_size: str = "250px"