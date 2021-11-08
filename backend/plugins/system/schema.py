from pydantic import BaseModel, Field


class System(BaseModel):
    """
    Collect System, CPU, Memory and Disk statistics 
    """

    per_cpu: bool = Field(
        True,
        title="Per CPU",
        description="Whether to report per-cpu stats or not",
        advanced=True
    )

    totalcpu: bool = Field(
        True,
        title="Total CPU",
        description="Whether to report total system cpu stats or not",
        advanced=True
    )
    
    collect_cpu_time: bool = Field(
        False,
        title="Collect CPU Time",
        description="If true, collect raw CPU time metrics",
        advanced=True
    )
    
    report_active: bool = Field(
        False,
        title="Report Active",
        description="If true, compute and report the sum of all non-idle CPU states",
        advanced=True
    )

    class Config:
        color: str = "#9400ff"
        icon: str = "fa fa-server"
    