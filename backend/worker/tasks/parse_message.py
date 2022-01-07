from ..mongo_connect import mongo_connect
from worker.main import app as celery_app
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


@celery_app.task(bind=True, name="parseMessage")
@mongo_connect
def parseMessage(self, data: str):
    self.update_state(state=celery.states.STARTED)

    data: dict = json.loads(data)
    for element in data:
        tags: dict = element["tags"]

        try:
            agent = Agent.objects(pk=element["agent_id"]).get()
        except Agent.DoesNotExist:
            self.update_state(state="PASSING")
            return

        # Execute Rules
        logger.debug(f"{agent.ip_address}, {element['measurement']}")
        rules = Rule.objects(enabled=True, agents__in=[agent], measurement=element["measurement"])
        for rule in rules:
            if rule.field not in tags.keys():
                continue
            
            executeRule.apply_async([str(rule.pk), str(agent.pk), json.dumps(tags)])

    self.update_state(state=celery.states.SUCCESS)
