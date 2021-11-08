from apps.agent.schema import AgentSchema
from apps.rule.schema import RuleSchema
from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from bson.objectid import ObjectId
from datetime import datetime
from typing import Any


class AlertSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    agent: PyObjectId = Field(default_factory=PyObjectId, alias="agent_id")
    rule: PyObjectId = Field(default_factory=PyObjectId, alias="agent_id")
    first_raise: datetime
    last_raise: datetime
    nb_raise: int
    priority: int
    ack: bool

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class AlertLineSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    alert: PyObjectId = Field(default_factory=PyObjectId, alias="alert_id")
    date: datetime
    metric: Any

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class AlertRuleSchema(AlertSchema):
    rule: RuleSchema
    agent: AgentSchema

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }