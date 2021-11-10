from pydantic import BaseModel, Field
from typing import List
import base64


class Postgresql(BaseModel):
    """Collect Postgresql's metrics"""

    url: str = Field(
        title="PostgreSQL URL",
        description="Exemple: postgres://telegraf@localhost/someDB"
    )

    ignored_database: List[str] = Field(
        [],
        title="Ignored Databases",
        description="List of databases to explicitly ignore",
        advanced=True
    )

    class Config:
        color: str = "#ef8383"
        with open("./plugins/postgresql/logo/postgresql.png", 'rb') as f:
            logo = f.read()

        img = base64.b64encode(logo)
        img_size: str = "340px"
