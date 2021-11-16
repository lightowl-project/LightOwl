from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from datetime import datetime, date
from typing import Optional
from bson import ObjectId


class APIKeyCreateSchema(BaseModel):
    expire: bool = False
    expire_at: date = datetime.now()


class APIKeySchema(APIKeyCreateSchema):
    id: Optional[PyObjectId] = Field(alias="_id")
    api_key: str
    created_at: datetime

    class Config:
        orm_mode: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }

class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    first_seen: datetime
    last_seen: datetime
    disabled: bool

    class Config:
        orm_mode: bool = True
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class UserUpdateSchema(BaseModel):
    username: str
    current_password: str = ""
    new_password: str = ""
    confirm_password: str = ""


class UserCreateSchema(BaseModel):
    username: str
    password: str
    confirm_password: str


class LightOwlInstallSchema(UserCreateSchema):
    ip_address: str
    lightowl_token: str

class UserUpdateSchema(BaseModel):
    disabled: bool
