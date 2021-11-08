from pydantic import BaseModel


class ConfigSchema(BaseModel):
    agent_token: str
    ip_address: str
    retention_duration: str

    class Config:
        orm_mode: bool = True


class RetentionSchema(BaseModel):
    retention_duration: str = "1w"


class MailSchema(BaseModel):
    auth: bool = False
    smtp_server: str = ""
    smtp_port: str = 587
    email: str = ""
    password: str = ""
    ssl: bool = False

    class Config:
        orm_mode: bool = True


class TwilioSchema(BaseModel):
    account_sid: str
    auth_token: str
    number_from: str

    class Config:
        orm_mode: bool = True


class MailTestSchema(MailSchema):
    to: str
    

class GeneralConfigSchema(BaseModel):
    config: ConfigSchema
    mail: MailSchema
    twilio: TwilioSchema

    class Config:
        orm_mode: bool = True
