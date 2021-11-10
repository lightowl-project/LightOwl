from pydantic import BaseModel
from datetime import datetime


class BaseLogSchema(BaseModel):
    date_start: datetime
    date_end: datetime
    measurement: str
    interval: str = "1m"
    agent: str = ""


class LogsSchema(BaseLogSchema):
    sort: str
    page: int
    per_page: int
    

class ChartSchema(BaseLogSchema):
    group_by: str = ""

