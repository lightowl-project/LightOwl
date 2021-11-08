from apps.agent.schema import AgentAlertSchema
from toolkits.bson import PyObjectId
from pydantic.fields import Field
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from typing import List



class HomeSchema(AgentAlertSchema):
    pass    


class WidgetSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    graph_type: str
    measurement: str
    field: str
    options: dict
    interval: str

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class WidgetCreateSchema(BaseModel):
    graph_type: str
    measurement: str
    field: str
    options: dict
    interval: str


class BaseWidgetDashboardSchema(BaseModel):
    x: int
    y: int
    w: int
    h: int
    i: int


class WidgetDashboardSchema(BaseModel):
    widget: WidgetSchema


class WidgetCreateDashboardSchema(BaseWidgetDashboardSchema):
    widget: WidgetCreateSchema


class DashboardSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    agent: PyObjectId = Field(default_factory=PyObjectId, alias="agent")
    name: str
    icon: str
    widgets: List[WidgetDashboardSchema]

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }



# class GeneralWidgetSchema(BaseModel):
#     agent: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     x: int
#     y: int
#     w: int
#     h: int

# class GeneralDashboardSchema(BaseModel):
#     id : PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     widgets: List[GeneralWidgetSchema]


# class GeneralWidgetCreateSchema(BaseModel):
#     agent: str
#     x: int
#     y: int
#     w: int
#     h: int


# class GeneralDashboardCreateSchema(BaseModel):
#     widgets: List[GeneralWidgetCreateSchema]

    
class DashboardCreateSchema(BaseModel):
    name: str
    widgets: List[WidgetCreateDashboardSchema]


class ExecuteQuerySchema(BaseModel):
    agent_id: str = ""
    measurement: str
    field: str
    group_by: str = ""
    agg: str = "mean"
    date_start: datetime = None
    date_end: datetime = None
    interval: str = None
    graph_type: str
 