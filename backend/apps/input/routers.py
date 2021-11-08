from .schema import InputCreateSchema, InputSchema, InputGenerateConfig, InputListSchema
from pydantic.error_wrappers import ValidationError as PydanticValidationError
from plugins.utils import get_plugin, get_plugin_config, plugins_list
from toolkits.paginate import TableParam, paginate
from mongoengine.errors import NotUniqueError
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from starlette.responses import Response
from ..common import BothAuthParams
from apps.agent.models import Agent
from fastapi import APIRouter, status
from plugins.plugins import Plugin
from toolkits.influx import Influx
from .models import Input

router: APIRouter = APIRouter()


@router.get("/plugins")
async def get_plugins_list(app = Depends(BothAuthParams)):
    return plugins_list()


@router.get("/")
async def get_inputs(all: bool = False, pagination: TableParam = Depends(), app = Depends(BothAuthParams)):
    if not all:
        result: dict = paginate(Input, pagination, InputSchema)
        return result

    data: list = []
    for input in Input.objects().order_by("name"):
        tmp = InputSchema(**input.to_mongo()).dict()
        plugin: Plugin = get_plugin(input.plugin_name)
        tmp["schema"] = get_plugin_config(plugin)
        data.append(InputListSchema(**tmp))

    return data


@router.get("/schema/")
async def get_plugin_schema(plugin_name: str, app = Depends(BothAuthParams)):
    plugin: Plugin = get_plugin(plugin_name)
    data: dict = plugin.SCHEMA.schema()
    return data


@router.get("/measurements/{agent_id}")
async def get_measurements(agent_id: str, app = Depends(BothAuthParams)):
    try:
        influx_client = Influx()
        return influx_client.get_measurements(agent_id)
    except Input.DoesNotExist:
        return HTTPException(status_code=404)


@router.get("/mapping/")
async def get_mapping(measurement: str, app = Depends(BothAuthParams)):
    influx_client = Influx()
    return influx_client.get_mapping(measurement)
   

@router.get("/tags/")
async def get_tags(measurement: str, app = Depends(BothAuthParams)):
    influx_client = Influx()
    tags: list = influx_client.get_tags(measurement)
    return tags


@router.get("/tag/values/")
async def get_tag_values(measurement: str, tag: str, app = Depends(BothAuthParams)):
    influx_client = Influx()
    values: list = influx_client.get_tag_values(measurement, tag)

    for agent in Agent.objects():
        values.append((str(agent.pk), agent.ip_address))

    return values


@router.post("/config/generate")
async def generate_plugin_config(plugin_config: InputGenerateConfig, app = Depends(BothAuthParams)):
    try:
        plugin: Plugin = get_plugin(plugin_config.plugin_name)(plugin_config) 
        config = plugin.generate_conf()
        return config    
    except PydanticValidationError as errors:
        error: dict = {}
        for err in errors.errors():
            error[err["loc"][0]] = err["msg"]

        raise HTTPException(status_code=400, detail=error)


@router.get("/{input_id}", response_model=InputSchema)
async def get_input(input_id: str, app = Depends(BothAuthParams)):
    try:
        input_obj = Input.objects(pk=input_id).get()
        return InputSchema(**input_obj.to_mongo())
    except Input.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_input(input_schema: InputCreateSchema, app = Depends(BothAuthParams)):
    try:
        agent = Agent.objects(pk=input_schema.agent_id).get()
        plugin: Plugin = get_plugin(input_schema.plugin_name)(input_schema)
        plugin.save(agent)
    except NotUniqueError:
        raise HTTPException(status_code=400, detail="UNIQUE")
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404)


@router.put("/{input_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_input(input_id: str, input_schema: InputCreateSchema, app = Depends(BothAuthParams)):
    try:
        input = Input.objects(pk=input_id).get()
        input.config = input_schema.config
        input.save()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Input.DoesNotExist:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND)


@router.delete("/{input_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_input(input_id: str, app = Depends(BothAuthParams)):
    try:
        input = Input.objects(pk=input_id).get()
        input.delete() 
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Input.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
