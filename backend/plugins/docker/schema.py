from pydantic import BaseModel, Field
from typing import List
import base64


class Docker(BaseModel):
    """
    Read metrics about docker containers. A command needs to be executed for this plugin on the host.<br/>
    You need to allow Telegraf user to access the Docker socket.<br/>
    <b>Run the following command on the host as root: usermad -aG docker telegraf</b>
    """

    endpoint: str = Field(
       "unix:///var/run/docker.sock",
       title="Docker Endpoint",
       description="To use TCP set: 'tcp://[ip]:[port]"
    )

    gather_services: bool = Field(
        False,
        title="Gather swarm metrics",
        description="Configure this only in one of the manager nodes in a Swarm cluster"
    )

    container_name_include: List[str] = Field(
        [],
        title="Containers names",
        description="Only collect metrics for these containers. If empty collects all"
    )

    container_name_exclude: List[str] = Field(
        [],
        title="Exclude",
        description="Don't collect metrics from these containers"
    )

    timeout: str = Field(
        "5s",
        title="Timeout",
        description="Timeout for docker list, info and stats commands",
        advanced=True
    )

    per_device: bool = Field(
        False,
        title="Gather metric per container"
    )

    class Config:
        url: str = "https://github.com/influxdata/telegraf/tree/master/plugins/inputs/docker"
        color: str = "#ef8383"
        with open("./plugins/docker/logo/docker.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "300px"
