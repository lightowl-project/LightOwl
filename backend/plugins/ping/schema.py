from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
import validators
import ipaddress


class MethodEnum(str, Enum):
    exec = "exec"
    native = "native"


class Ping(BaseModel):
    """
    Sends a ping message by executing the system ping command and reports the results.<br/>
    This plugin has two main methods of operation: exec and native. The recommended method is native, which has greater system compatibility and performance. However, for backwards compatibility the exec method is the default.<br/>
    When using method = "exec", the systems ping utility is executed to send the ping packets.
    """

    urls: List[str] = Field(
        title="URLs",
        description="Hosts to send ping packets to"
    )

    method: MethodEnum = Field(
        'exec',
        title="Method",
        description='Method used for sending pings, can be either "exec" or "native".  When set to "exec" the systems ping command will be executed. <br/>When set to "native" the plugin will send pings directly.<br/>While the default is "exec" for backwards compatibility, new deployments are encouraged to use the "native" method for improved compatibility and performance',
        advanced=True
    )

    count: int = Field(
        1,
        title="Count",
        description="Number of ping packets to send per interval",
        min=1,
        advanced=True
    )

    ping_interval: float = Field(
        1.0,
        title="Ping Interval",
        description="Time to wait between sending ping packets in seconds",
        min=1.0,
        advanced=True
    )

    timeout: Optional[float] = Field(
        1.0,
        title="Timeout",
        description="If set, the time to wait for a ping response in seconds",
        min=1.0,
        advanced=True
    )

    deadline: Optional[int] = Field(
        10,
        title="Deadline",
        description="If set, the total ping deadline, in seconds",
        advanced=True
    )

    interface: Optional[str] = Field(
        title="Interface",
        description="Interface or source address to send ping from",
        advanced=True
    )

    percentiles: List[int] = Field(
        [50, 95, 99],
        title="Percentiles",
        description="Percentiles to calculate. This only works with the native method",
        advanced=True
    )

    binary: str = Field(
        "ping",
        title="Binary",
        description="Specify the ping executable binary",
        advanced=True
    )

    arguments: List[str] = Field(
        ["-c", "3"],
        title="Arguments",
        description="Arguments for ping command",
        advanced=True
    )

    ipv6: bool = Field(
        False,
        title="IPV6",
        description="Use only IPv6 addresses when resolving a hostname",
        advanced=True
    )

    size: int = Field(
        56,
        title="Size",
        description="Number of data bytes to be sent",
        advanced=True
    )

    @validator("urls")
    def validate_urls(cls, v):
        for i in v:
            try:
                ipaddress.ip_address(i)
            except ValueError:
                if not validators.domain(i):
                    raise ValueError(f"{i} is not a valid IP Address or Domain")

        return v
    
    class Config:
        color: str = "#f49b51"
        icon: str = "fa fa-paper-plane"
        metrics: dict = {
            "result_code": "success = 0, no such host = 1, ping error = 2"
        }
