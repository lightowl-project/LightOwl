from pydantic.networks import IPvAnyAddress
from toolkits.bson import PyObjectId
from typing import List, Optional
from pydantic import BaseModel
from pydantic.fields import Field
from datetime import datetime
from bson import ObjectId


class AgentSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hostname: str
    ip_address: IPvAnyAddress
    last_seen: Optional[datetime]
    tags: List[str] = []
    os: str

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class AgentJoinSchema(BaseModel):
    hostname: str
    os: str
    tags: List[str]
    plugins: dict


class AgentAlertSchema(AgentSchema):
    from apps.alert.schema import AlertSchema
    alerts: List[AlertSchema] = []
    

class UpdateAgentSchema(BaseModel):
    tags: List[str]
