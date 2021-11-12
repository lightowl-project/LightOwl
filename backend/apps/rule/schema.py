from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from bson.objectid import ObjectId
from datetime import datetime
from typing import Any, List
from enum import Enum


class OperatorChoices(str, Enum):
    eq = "eq"
    neq = "neq"
    lt = "lt"
    lte = "lte"
    gt = "gt"
    gte = "gte"
    contains = "contains"
    notcontains = "notcontains"
    startswith = "startswith"
    endswith = "endswith"

class RuleSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    enabled: bool
    name: str = ""
    priority: int = 3
    created_at: datetime
    updated_at: datetime
    agents: List[PyObjectId]
    measurement: str
    field: str
    operator: OperatorChoices
    pattern: Any
    duration: str
    description: str = ""
    remediation: str = ""
    nb_raise: int = 0
    sendMail: bool = False
    sendSMS: bool = False
    mailTo: List[str] = []
    smsTo: List[str] = []

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class RuleAgentSchema(RuleSchema):
    from apps.agent.schema import AgentSchema
    agents: List[AgentSchema]


class RuleCreateSchema(BaseModel):
    enabled: bool
    priority: int
    agents: List[str]
    measurement: str
    field: str
    operator: OperatorChoices
    pattern: Any
    duration: str
    name: str = ""
    description: str = ""
    remediation: str = ""
    sendMail: bool = False
    sendSMS: bool = False
    mailTo: List[str] = []
    smsTo: List[str] = []


class RuleUpdateSchema(BaseModel):
    enabled: bool
    priority: int
    measurement: str
    field: str
    operator: OperatorChoices
    pattern: Any
    duration: str
    name: str = ""
    description: str = ""
    remediation: str = ""
    sendMail: bool = False
    sendSMS: bool = False
    mailTo: List[str] = []
    smsTo: List[str] = []

class EnableDisableRuleSchema(BaseModel):
    rule: str
    enabled: bool
