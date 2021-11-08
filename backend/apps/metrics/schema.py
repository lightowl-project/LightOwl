from pydantic import BaseModel
from datetime import datetime



class LogsSchema(BaseModel):
    dateStart: datetime
    dateEnd: datetime
    measurement: str
    interval: str = "1m"
    sort: str
    page: int
    per_page: int
    agent: str = ""
    