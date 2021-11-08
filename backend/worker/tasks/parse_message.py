from ..mongo_connect import mongo_connect
from apps.agent.models import Agent
from apps.rule.models import Rule
from .rules import executeRule
from config import settings
import logging.config
import logging
import celery
import json

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("celery")


@celery.task(bind=True, name="parseMessage")
@mongo_connect
def parseMessage(self, data: str):
    data: dict = json.loads(data)
    for element in data:
        tags: dict = element["tags"]

        self.update_state(state=celery.states.STARTED)

        try:
            agent = Agent.objects(pk=element["agent_id"]).get()
        except Agent.DoesNotExist:
            self.update_state(state="PASSING")
            return

        # Execute Rules
        rules = Rule.objects(enabled=True, agent=agent, measurement=element["measurement"])
        for rule in rules:
            if rule.field not in tags.keys():
                continue
            
            executeRule.apply_async([str(rule.pk), json.dumps(tags)])

        self.update_state(state=celery.states.SUCCESS)
