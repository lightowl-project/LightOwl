import mongoengine

RETENTION_CHOICES: tuple = (
    ("1d", "1d"),
    ("1w", "1w"),
    ("2w", "2w"),
    ("3w", "3w"),
    ("4w", "4w"),
    ("12w", "12w"),
)

class Config(mongoengine.Document):
    ip_address = mongoengine.StringField()
    agent_token = mongoengine.StringField()
    retention_duration = mongoengine.StringField(choices=RETENTION_CHOICES, default="1w")


class MailSettings(mongoengine.Document):
    auth = mongoengine.BooleanField(default=False)
    smtp_server = mongoengine.StringField(default="")
    smtp_port = mongoengine.IntField(default=587)
    email = mongoengine.StringField(default="")
    password = mongoengine.StringField(default="")
    ssl = mongoengine.BooleanField(default=False)
    

class TwilioSettings(mongoengine.Document):
    account_sid = mongoengine.StringField(default="")
    auth_token = mongoengine.StringField(default="")
    number_from = mongoengine.StringField(default="")
    