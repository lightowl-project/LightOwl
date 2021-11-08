from pydantic import BaseModel, Field
from typing import List
import base64


class MongoDB(BaseModel):
    """Collect MongoDB Statistics"""

    urls: List[str] = Field(
        title="URLs",
        description="URLs of Mongo exemple: mongodb://127.0.0.1:27017"
    )

    gather_cluster_status: bool = Field(
        False,
        title="Gather Cluster Status",
        description="Collect MongoDB Cluster Status"
    )

    gather_perdb_stats: bool = Field(
        False,
        title="Collect per database stats ",
        advanced=True
    )

    gather_col_stats: bool = Field(
        False,
        title="Collect per collection stats",
        advanced=True
    )

    gather_top_stat: bool = Field(
        False,
        title="Collect usage statistics for each collection",
        description="Insert, Update, Queries, Remove, Getmore, Command....",
        advanced=True
    )

    col_stats_dbs: List[str] = Field(
        [],
        title="List of database where collections stats are collected",
        advanced=True
    )

    class Config:
        color: str = "#70b548"
        with open("./plugins/mongodb/logo/mongodb.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "90px"
