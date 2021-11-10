from pydantic import BaseModel, Field
from enum import Enum
from typing import List
import base64


class HealthLevelEnum(str, Enum):
    indices = "indices"
    cluster = "cluster"


class Elasticsearch(BaseModel):
    """Collect statistics from Elasticsearch"""

    urls: List[str] = Field(
        title="List of Elasticsearch servers",
        description="Example: http://user:pass@localhost:9200"
    )

    insecure_skip_verify: bool = Field(
        False,
        title="Skip SSL Certificate Verification"
    )

    http_timeout: str = Field(
        default="5s",
        title= "HTTP Timeout",
        description="Timeout for HTTP requests to the elastic search server(s)"
    )

    local: bool = Field(
        True,
        title="Local gathering",
        description="When true, the node will read only its own stats. Set this to false when you want to read the node stats from all nodes of the cluster"
    )

    cluster_health: bool = Field(
        True,
        title="Gather Cluster Health"
    )

    cluster_stats: bool = Field(
        True,
        title="Gather Cluster statistics"
    )

    cluster_stats_only_from_master: bool = Field(
        True,
        title="Gather Cluster Stats from the master Node",
        description="To work this require local = true"
    )

    indices_include: List[str] = Field(
        ["_all"],
        title="Indices to collect",
        description="Can be one or more indices name or _all. Use of wildcards is allowed. Use a wildcard at the end to retreive index names that end with a changing value, like a date"
    )

    cluster_health_level: HealthLevelEnum = Field(
        "indices",
        title="Cluster Health Level",
        description="Adjust cluster_health_level when you want to obtain detailed health stats",
        advanced=True
    )

    node_stats: List[str] = Field(
        [],
        title="Sub stats to be gathered",
        description="Valid options are: indices, os, process, jvm, thread_pool, fs, transport, http, breaker",
        advanced=True
    )

    username: str = Field(
        "",
        title="Elasticsearch Username",
        advanced=True
    )

    password: str = Field(
        "",
        title="Elasticsearch Password",
        advanced=True
    )
        
    class Config:
        color: str = "#83dbd3"
        with open("./plugins/elasticsearch/logo/elasticsearch.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "300px"
