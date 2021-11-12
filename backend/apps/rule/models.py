from apps.agent.models import Agent
from datetime import datetime
import mongoengine


OPERATOR_CHOICES: tuple = (
    ("gte", "gte"),
    ("lte", "lte"),
    ("gt", "gt"),
    ("lt", "lt"),
    ("eq", "eq"),
    ("neq", "neq"),
    ("contains", "contains"),
    ("notcontains", "notcontains"),
    ("startswith", "startswith"),
    ("endswith", "endswith")
)

DURATION_CHOICES: tuple = (
    ("oneshot", "oneshot"),
    ("1m", "1m"),
    ("5m", "5m"),
    ("10m", "10m"),
    ("1h", "1h"),
    ("2h", "2h"),
    ("6h", "6h")
)


class Rule(mongoengine.DynamicDocument):
    enabled = mongoengine.BooleanField(default=True)
    priority = mongoengine.IntField(default=3)
    name = mongoengine.StringField(default="")
    created_at = mongoengine.DateTimeField(default=datetime.now)
    updated_at = mongoengine.DateTimeField(default=datetime.now)
    description = mongoengine.StringField(default="")
    remediation = mongoengine.StringField(default="")
    agents = mongoengine.ListField(mongoengine.ReferenceField(Agent, reverse_delete_rule=mongoengine.CASCADE))
    measurement = mongoengine.StringField()
    field = mongoengine.StringField()
    operator = mongoengine.StringField(choices=OPERATOR_CHOICES)
    pattern = mongoengine.DynamicField()
    duration = mongoengine.StringField(choices=DURATION_CHOICES)
    nb_raise = mongoengine.IntField(default=0)
    sendMail = mongoengine.BooleanField()
    sendSMS = mongoengine.BooleanField()
    mailTo = mongoengine.ListField(mongoengine.StringField())
    smsTo = mongoengine.ListField(mongoengine.StringField())
