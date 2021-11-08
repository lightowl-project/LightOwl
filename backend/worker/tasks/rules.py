from toolkits.exceptions import InvalidOperator, MailSettingsNotConfigured
from apps.config.models import Config, MailSettings
from worker.mongo_connect import mongo_connect
from toolkits.rabbitmq.rabbit import push_message
from apps.alert.models import Alert, AlertLine
from apps.config.schema import MailSchema
from datetime import datetime, timedelta
from toolkits.mail import MailToolkit
from apps.rule.models import Rule
from toolkits.influx import Influx
from config import settings
from typing import Any
from redis import Redis
import logging.config
import logging
import celery
import json

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("celery")


def get_redis_client() -> Redis:
    return Redis(host=settings.REDIS_URL, port=settings.REDIS_PORT, decode_responses=True)


def execute_operator(metric: str, operator: str, pattern: Any) -> bool:
    if operator == "eq":
        return metric == pattern
    elif operator == "neq":
        return metric != pattern
    elif operator == "gt":
        return float(metric) > float(pattern)
    elif operator == "gte":
        return float(metric) >= float(pattern)
    elif operator == "lt":
        return float(metric) < float(pattern)
    elif operator == "lte":
        return float(metric) <= float(pattern)
    elif operator == "contains":
        return str(pattern) in str(metric)
    elif operator == "notcontains":
        return str(pattern) not in str(metric)
    elif operator == "startswith":
        return str(metric).startsWith(str(pattern))
    elif operator == "endswith":
        return str(metric).endsWith(str(pattern))
    else:
        raise InvalidOperator()


def send_mail(alert: Alert) -> bool:
    try:
        mail_config = MailSettings.objects.get()
    except MailSettings.DoesNotExist:
        raise MailSettingsNotConfigured()

    config = Config.objects.get()

    mail_toolkit = MailToolkit(MailSchema(**mail_config.to_mongo()))

    subject: str = f"[LIGHTOWL] Alert on {alert.agent.ip_address}"
    body: str = f"""<html><body>
<p>Rule {alert.rule.name} raised an alert on Agent: {alert.agent.ip_address}</p>
<p>You can see the alert <a href="https://{config.ip_address}/#/agents/{str(alert.agent.pk)}">here</a></p>
</body></html>"""
    
    mail_toolkit.send(alert.rule.mailTo, subject, body)


def throw_alert(rule: Rule, metric: Any, pattern: Any):
    logger.info(f"Raising alert for Rule {str(rule.pk)} Metric: {metric} Pattern: {pattern}")

    try:
        alert = Alert.objects(rule=rule, priority=rule.priority).get()
        alert.nb_raise += 1
        alert.last_raise = datetime.utcnow()
        alert.save()
    except Alert.DoesNotExist:
        alert = Alert.objects.create(
            rule=rule,
            priority=rule.priority,
            agent=rule.agent
        )

        message: dict = {
            "alert": str(alert.pk),
            "agent_id": str(alert.agent.pk),
            "rule": alert.rule.name,
            "agent": alert.agent.ip_address,
            "priority": alert.priority,
            "metric": metric
        }

        push_message(message)
        if rule.sendMail:
            send_mail(alert)

    AlertLine.objects.create(
        alert=alert,
        date=datetime.utcnow(),
        metric=metric
    )


def check_duration(rule: Rule, metric: Any, pattern: Any):
    try:
        # Check if an alert already exists:
        Alert.objects(rule=rule, priority=rule.priority).get()
        throw_alert(rule, metric, pattern)
        return
    except Alert.DoesNotExist:
        pass

    redis_conn: Redis = get_redis_client()

    data = redis_conn.hgetall(str(rule.pk))
    if not data:
        date = datetime.timestamp(datetime.utcnow())
        redis_conn.hmset(str(rule.pk), {"date": date})
        return
    
    date_first_raise = datetime.fromtimestamp(float(data["date"]))
    date_now = datetime.utcnow()

    if rule.duration == "1m":
        date_minus_duration = date_now - timedelta(minutes=1)
    elif rule.duration == "5m":
        date_minus_duration = date_now - timedelta(minutes=5)
    elif rule.duration == "10m":
        date_minus_duration = date_now - timedelta(minutes=10)
    elif rule.duration == "1h":
        date_minus_duration = date_now - timedelta(hours=1)
    elif rule.duration == "2h":
        date_minus_duration = date_now - timedelta(hours=2)
    elif rule.duration == "6h":
        date_minus_duration = date_now - timedelta(hours=6)

    logger.info(f"Rule [{str(rule.pk)}][{rule.name}] raise since {date_first_raise.isoformat()}")
    if date_first_raise <= date_minus_duration:
        throw_alert(rule, metric, pattern)


@celery.task(bind=True, name="executeRule")
@mongo_connect
def executeRule(self, rule_id: str, tags: str):
    self.update_state(state=celery.states.STARTED)

    try:
        tags: dict = json.loads(tags)
        rule = Rule.objects(pk=rule_id).get()
        metric = tags[rule.field]
        operator: str = rule.operator
        pattern: Any = rule.pattern

        influx_client = Influx()
        metric_type = influx_client.get_mapping(rule.measurement)[rule.field]

        if metric_type == "float":
            metric = float(metric)
        elif metric_type == "int":
            metric = int(metric)

        if not execute_operator(metric, operator, pattern):
            redis_conn: Redis = get_redis_client()
            redis_conn.delete(str(rule.pk))

            self.update_state(state=celery.states.SUCCESS)
            return

        if rule.duration == "oneshot":
            # Throw alert
            throw_alert(rule, metric, pattern)
        else:
            check_duration(rule, metric, pattern)

    except Exception as error:
        logger.critical(error, exc_info=1)
        self.update_state(state=celery.states.FAILURE)
        raise celery.exceptions.Ignore()
