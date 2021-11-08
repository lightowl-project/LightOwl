from fastapi import APIRouter, HTTPException, status
from apps.alert.schema import AlertRuleSchema
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from mongoengine.queryset.visitor import Q
from apps.rule.schema import RuleSchema
from toolkits.paginate import TableParam
from ..common import BothAuthParams
from apps.agent.models import Agent
from .models import Alert, AlertLine
from bson.objectid import ObjectId
from apps.rule.models import Rule
from config import settings
from redis import Redis
import logging.config
import logging
import math

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.get("/")
async def get_alerts(priority: int = None, agent_id: str = None, pagination: TableParam = Depends(), app = Depends(BothAuthParams)):
    per_page: int = pagination.per_page
    page: int = pagination.page
    sort_field, order = pagination.sort.split("|")

    order_dir: dict = {
        "ascending": 1,
        "descending": -1,
        "desc": -1,
        "asc": 1
    }

    query = {}
    if priority:
        query["priority"] = priority

    if agent_id:
        query["agent"] = ObjectId(agent_id)

    if pagination.search:
        query["$or"] = [
            {"agent.ip_address": {"$regex": f".*{pagination.search}.*", "$options": "i"}},
            {"agent.hostname": {"$regex": f".*{pagination.search}.*", "$options": "i"}},
            {"agent.tags": {"$in": pagination.search}}
        ]

    lookup: list = [{
        "$lookup": {
            "from": "rule",
            "localField": "rule",
            "foreignField": "_id",
            "as": "rule"
        }
    }, {
        "$lookup": {
            "from": "agent",
            "localField": "agent",
            "foreignField": "_id",
            "as": "agent"
        }
    }]

    skip: int = (page-1) * per_page

    aggs = [
        {"$match": query},
        {"$skip": skip},
        {"$limit": per_page},
        {"$sort": { sort_field: order_dir.get(order, -1)}},
        *lookup
    ]

    data_tmp = Alert.objects.aggregate(*aggs)

    try:
        count_agg: list = [
            {"$match": query},
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]
        total_objects: int = list(Alert.objects.aggregate(*count_agg))[0]["count"]
    except IndexError:
        total_objects: int = 0

    data: list = []    
    for tmp in data_tmp:
        tmp["rule"] = tmp["rule"][0]
        tmp["agent"] = tmp["agent"][0]

        data.append(jsonable_encoder(AlertRuleSchema(**tmp)))

    return {
        "data": data,
        "from": skip,
        "current_page": page,
        "per_page": per_page,
        "to": skip + len(data),
        "total": total_objects,
        "last_pages": math.ceil(total_objects / per_page)
    }


@router.get("/{alert_id}", response_model=AlertRuleSchema)
async def get_alert_by_id(alert_id: str, app = Depends(BothAuthParams)):
    try:
        alert = Alert.objects(pk=alert_id).get()

        data = alert.to_mongo()
        data["rule"] = alert.rule.to_mongo()
        data['agent'] = alert.agent.to_mongo()

        tmp = AlertRuleSchema(**data)
        return tmp
    
    except Alert.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/by_agent/{agent_id}")
async def get_alerts_by_agent(agent_id: str, ack: bool = None, app = Depends(BothAuthParams)):
    try:
        agent = Agent.objects(pk=agent_id).get()
        filter = Q(agent=agent)
        if ack is not None:
            filter &= Q(ack=ack)

        alerts: list = []
        for doc in Alert.objects(filter):
            doc = doc.to_mongo()
            doc["rule"] = [RuleSchema(**Rule.objects(pk=doc["rule"]).get().to_mongo())]
            alerts.append(doc)

        return alerts
    except Agent.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/{alert_id}/graph", include_in_schema=False)
async def get_alert_graph(alert_id: str, app = Depends(BothAuthParams)):
    try:
        alert = Alert.objects(pk=alert_id).get()

        data: list = []
        for alert_line in AlertLine.objects(alert=alert).order_by("date"):
            data.append((alert_line.date, float(alert_line.metric)))

        return {
            "data": data,
            "field": f"{alert.rule.measurement}.{alert.rule.field}"
        }
    except Alert.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, app = Depends(BothAuthParams)):
    try:
        alert = Alert.objects(pk=alert_id).get()

        redis_cli: Redis = Redis(host=settings.REDIS_URL, port=settings.REDIS_PORT, decode_responses=True)
        redis_cli.delete(str(alert.rule.pk))        
        alert.delete()

    except Alert.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
