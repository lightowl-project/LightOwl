from apps.agent.models import Agent
from apps.rule.models import Rule
from datetime import datetime
import mongoengine




class Alert(mongoengine.Document):
    agent = mongoengine.ReferenceField(Agent, reverse_delete_rule=mongoengine.CASCADE)
    rule = mongoengine.ReferenceField(Rule, reverse_delete_rule=mongoengine.CASCADE)
    first_raise = mongoengine.DateTimeField(default=datetime.utcnow)
    last_raise = mongoengine.DateTimeField(default=datetime.utcnow)
    nb_raise = mongoengine.IntField(default=1)
    priority = mongoengine.IntField(default=3, unique_with=("rule", "agent"))
    ack = mongoengine.BooleanField(default=False)


class AlertLine(mongoengine.Document):
    alert = mongoengine.ReferenceField(Alert, reverse_delete_rule=mongoengine.CASCADE)
    date = mongoengine.DateTimeField()
    metric = mongoengine.DynamicField()