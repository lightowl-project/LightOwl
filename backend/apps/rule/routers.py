from .schema import EnableDisableRuleSchema, RuleCreateSchema, RuleSchema, RuleUpdateSchema, RuleAgentSchema
from fastapi import APIRouter, HTTPException, status
from worker.tasks.rules import get_redis_client
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from apps.common import BothAuthParams
from toolkits.paginate import TableParam
from starlette.responses import Response
from apps.agent.models import Agent
from datetime import datetime
from config import settings
from bson import ObjectId
from .models import Rule
import logging.config
import logging
import math

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.get("/")
async def get_rules(agent_id: str = None, pagination: TableParam = Depends(), app = Depends(BothAuthParams)) -> dict:
    per_page: int = pagination.per_page
    page: int = pagination.page
    sort_field, order = pagination.sort.split("|")

    order_dir: dict = {
        "ascending": 1,
        "descending": -1,
        "desc": -1,
        "asc": 1
    }

    query: dict = {}
    if pagination.search:
        query["name"] = {"$regex": f".*{pagination.search}.*", "$options": "i"}
        
    if agent_id:
        query["agents"] = {"$in": [ObjectId(agent_id)]}

    lookup: dict = {
        "from": "agent",
        "localField": "agent",
        "foreignField": "_id",
        "as": "agent"
    }

    skip: int = (page-1) * per_page

    aggs: list = [
        {"$match": query},
        {"$skip": skip},
        {"$limit": per_page},
        {"$sort": { sort_field: order_dir.get(order, -1)}},
        {"$lookup": lookup},
    ]

    data_tmp = Rule.objects.aggregate(*aggs)

    try:
        count_agg: list = [
            {"$match": query},
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]
        total_objects: int = list(Rule.objects.aggregate(*count_agg))[0]["count"]
    except IndexError:
        total_objects: int = 0

    data: list = []    
    for tmp in data_tmp:
        tmp["agents"] = list(Agent.objects(pk__in=tmp["agents"]))
        data.append(jsonable_encoder(RuleAgentSchema(**tmp)))

    return {
        "data": data,
        "from": skip,
        "current_page": page,
        "per_page": per_page,
        "to": skip + len(data),
        "total": total_objects,
        "last_pages": math.ceil(total_objects / per_page)
    }


@router.get("/{rule_id}", response_model=RuleSchema)
async def get_rule(rule_id: str, app = Depends(BothAuthParams)):
    try:
        return Rule.objects(pk=rule_id).get().to_mongo()
    except Rule.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rule(form: RuleCreateSchema, app = Depends(BothAuthParams)):
    try:
        rule = Rule(**form.dict())
        rule.agents = list(Agent.objects(pk__in=form.agents))
        rule.save()
    except Exception as err:
        raise


@router.put("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_rule(rule_id: str, form: RuleUpdateSchema, app = Depends(BothAuthParams)):
    try:
        rule = Rule.objects(pk=rule_id).get()
        rule.name = form.name
        rule.measurement = form.measurement 
        rule.field = form.field 
        rule.operator = form.operator 
        rule.pattern = form.pattern 
        rule.duration = form.duration 
        rule.sendMail = form.sendMail
        rule.sendSMS = form.sendSMS
        rule.mailTo = form.mailTo
        rule.smsTo = form.smsTo
        rule.updated_at = datetime.utcnow()
        rule.save()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Rule.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@router.post("/enable", status_code=status.HTTP_204_NO_CONTENT)
async def enable_disable_rule(form: EnableDisableRuleSchema, app = Depends(BothAuthParams)):
    try:
        rule = Rule.objects(pk=form.rule).get()
        rule.enabled = form.enabled

        if not form.enabled:
            redis_conn = get_redis_client()
            redis_conn.delete(str(rule.pk))

        rule.updated_at = datetime.utcnow()
        rule.save()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Rule.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: str, app = Depends(BothAuthParams)):
    try:
        rule = Rule.objects(pk=rule_id).get()
        redis_conn = get_redis_client()
        redis_conn.delete(str(rule.pk))
        rule.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except Rule.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/data/mailsms", include_in_schema=True)
async def get_emails_sms_list(app = Depends(BothAuthParams)):
    emails: list = []
    phones: list = []

    results = Rule.objects.all().only(*("mailTo", "smsTo"))
    for result in results:
        emails.extend(result.mailTo)
        phones.extend(result.smsTo)

    return {
        "emails": set(emails),
        "phones": set(phones)
    }
