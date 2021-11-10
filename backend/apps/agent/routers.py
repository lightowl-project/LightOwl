from .schema import AgentSchema, AgentJoinSchema, AgentAlertSchema, UpdateAgentSchema
from apps.common import BothAuthParams, AgentAuthParams
from starlette.responses import FileResponse, Response
from plugins.utils import get_plugin, get_plugin_config
from toolkits.paginate import TableParam, paginate
from apps.input.schema import InputCreateSchema
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Request, status
from fastapi.param_functions import Depends
from apps.input.schema import InputSchema
from apps.alert.schema import AlertSchema
from apps.config.models import Config
from apps.input.models import Input
from apps.alert.models import Alert
from plugins.plugins import Plugin
from datetime import datetime
from config import settings
from .models import Agent
from typing import List
import logging.config
import tempfile
import logging
import jinja2
import shutil
import os

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


def make_archive(source, destination):
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s'%(name,format), destination)


@router.post("/join")
async def agent_join(agent_join_schema: AgentJoinSchema, request: Request, app = Depends(AgentAuthParams)):
    client_ip = request.headers["x-forwarded-for"]

    agent = Agent(
        hostname=agent_join_schema.hostname,
        os=agent_join_schema.os,
        tags=agent_join_schema.tags,
        ip_address=client_ip,
    )

    agent.save()

    # All agents have at minimum the system plugin enabled
    agent_join_schema.plugins["system"] = {}

    for plugin_name, plugin_config in agent_join_schema.plugins.items():
        input_obj = Input(
            plugin_name=plugin_name,
            config=plugin_config
        )

        tmp = input_obj.to_mongo()
        tmp["agent_id"] = str(agent.pk)
        plugin = get_plugin(plugin_name)(InputCreateSchema(**tmp))
        plugin.save(agent)

    config = Config.objects.get()
    data_env: dict = {
        "rabbit_password": settings.RABBITMQ_PASSWORD,
        "agent_token": config.agent_token,
        "ip_address": config.ip_address,
        "agent_id": str(agent.pk)
    }

    with open("/app/toolkits/agent/.env.j2", 'r') as f:
        template = f.read()
        env = jinja2.Template(template).render(data_env)

    with open("/app/toolkits/agent/telegraf.conf.j2", 'r') as f:
        template = f.read()
        telegraf = jinja2.Template(template).render(data_env)

    dir_name: str = "/tmp/lightowl"
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

    os.makedirs(dir_name)
    with open(f"{dir_name}/.env", 'w') as f:
        f.write(env)

    with open(f"{dir_name}/telegraf.conf", 'w') as f:
        f.write(telegraf)

    with open(f"{dir_name}/lightowl.conf", "w") as f:
        lightowl_conf = await get_agent_config(str(agent.pk), app)
        f.write(lightowl_conf)
    
    shutil.copyfile("/etc/ssl/lightowl/ca.pem", f"{dir_name}/ca.pem")
    # with tarfile.open("/tmp/lightowl.tar.gz","w:gz") as tar:
    #     tar.add(dir_name, arcname=os.path.basename(dir_name))
    make_archive(dir_name, "/tmp/lightowl-agent.zip")
    return FileResponse("/tmp/lightowl-agent.zip")


@router.get("/")
async def get_agents(all: bool = False, pagination: TableParam = Depends(), app = Depends(BothAuthParams)):
    if all:
        return [AgentSchema(**a.to_mongo()) for a in Agent.objects()]

    result: dict = paginate(Agent, pagination, AgentSchema)#, search={"hostname": {"$ne": "LightOwl Server"}})
    return result


@router.get("/{agent_id}", response_model=AgentAlertSchema)
async def get_agent(agent_id: str, alerts: bool = False, app = Depends(BothAuthParams)):
    try:
        agent = Agent.objects(pk=agent_id).get()

        if alerts:
            alerts_list = [AlertSchema(**doc.to_mongo()) for doc in Alert.objects(agent=agent, ack=False)]
            agent = agent.to_mongo()
            agent["alerts"] = alerts_list

        return agent
    except Agent.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    

@router.put("/{agent_id}", response_model=AgentSchema)
async def update_agent(agent_id: str, update_schema: UpdateAgentSchema, app = Depends(BothAuthParams)):
    try:
        agent = Agent.objects(pk=agent_id).get()
        agent.tags = list(set(update_schema.tags))
        agent.save()

        return agent
    except Agent.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, app = Depends(BothAuthParams)):
    try:
        agent = Agent.objects(pk=agent_id).get()
        agent.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Agent.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/config/{agent_id}")
async def get_agent_config(agent_id: str, app = Depends(AgentAuthParams)):
    try:
        agent = Agent.objects(pk=agent_id).get()
        agent.last_seen = datetime.utcnow()
        agent.save()

        config: list = []
        for input_obj in Input.objects(agent=agent):
            plugin: Plugin = get_plugin(input_obj.plugin_name)(input_obj)
            config.append(plugin.generate_conf())

        return "\n\n".join(config)
 
    except Agent.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/inputs/{agent_id}", response_model=List[InputSchema])
async def get_agent_inputs(agent_id: str, app = Depends(BothAuthParams)):
    try:
        agent = Agent.objects(pk=agent_id).get()
        tmp_inputs = Input.objects(agent=agent)
        inputs: list = []

        for tmp in tmp_inputs:
            tmp = InputSchema(**tmp.to_mongo())
            plugin = get_plugin(tmp.plugin_name)
            tmp.plugin = get_plugin_config(plugin)
            inputs.append(tmp)

        return inputs
    except Agent.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
