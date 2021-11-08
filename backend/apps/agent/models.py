from datetime import datetime
import mongoengine


class Agent(mongoengine.DynamicDocument):
    hostname = mongoengine.StringField()
    ip_address = mongoengine.StringField(unique=True)
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    last_seen = mongoengine.DateTimeField(default=datetime.utcnow)
    os = mongoengine.StringField()
    tags = mongoengine.ListField(mongoengine.StringField())
