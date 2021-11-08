from apps.agent.models import Agent
from plugins.utils import get_plugin
from datetime import datetime
import mongoengine


class Input(mongoengine.Document):
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    updated_at = mongoengine.DateTimeField(default=datetime.utcnow)
    plugin_name = mongoengine.StringField()
    config = mongoengine.DictField()
    agent = mongoengine.ReferenceField(Agent, unique_with=("plugin_name",), reverse_delete_rule=mongoengine.CASCADE)
    

    def get_plugin(self):
        return get_plugin(self.plugin_name)(self)
