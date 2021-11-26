import base64
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import validators
import ipaddress


class RabbitMQ(BaseModel):
    """
    Reads metrics from RabbitMQ servers via the Management Plugin.
    """

    url: str = Field(
        title="URL",
        description="URL of RabbitMQ Management plugin"
    )

    username: Optional[str] = Field(
        title="Username",
    )

    password: Optional[str] = Field(
        title="Password",
    )

    header_timeout: int = Field(
        3,
        title="Response Header Timeout",
        description="If non-zero, specifies the amount of time to wait for a server's response headers after fully writing the request",
        min=1
    )

    client_timeout: int = Field(
        4,
        title="Client Timeout",
        description="specifies a time limit for requests made by this client. Includes connection time, any redirects, and reading the response body",
        min=1
    )

    nodes: List[str] = Field(
        [],
        title="Nodes",
        description="Nodes to gather as the rabbitmq_node measurement. If not specified, metrics for all nodes are gathered",
        advanced=True
    )

    queues: List[str] = Field(
        [],
        title="List of queues",
        description="Queues to gather as the rabbitmq_queue measurement. If not specified, metrics for all queues are gathered",
        advanced=True
    )
   
    exchange: List[str] = Field(
        [],
        title="List of exchanges",
        description="Exchanges to gather as the rabbitmq_exchange measurement. If not specified, metrics for all exchanges are gathered",
        advanced=True
    )

    insecure_skip_verify: Optional[bool] = Field(
        False,
        title="Insecure Skip Verify",
        description="Use TLS but skip chain & host verification"
    )
    
    class Config:
        url: str = "https://github.com/influxdata/telegraf/tree/master/plugins/inputs/rabbitmq"
        color: str = "#70b548"
        with open("./plugins/rabbitmq/logo/rabbitmq.png", 'rb') as f:
            logo = f.read()

        img: str = base64.b64encode(logo)
        img_size: str = "300px"
