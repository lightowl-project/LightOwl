from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from bson.objectid import ObjectId
from typing import Any, Optional
from datetime import datetime



class InputSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: datetime
    plugin_name: str
    config: Any
    plugin: Optional[Any] = {}

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class InputListSchema(InputSchema):
    configuration: dict = Field(alias="schema")


class InputCreateSchema(BaseModel):
    agent_id: str
    plugin_name: str
    config: Any


class InputConfigSchema(BaseModel):
    plugin_name: str


class InputGenerateConfig(BaseModel):
    plugin_name: str
    config: Any
