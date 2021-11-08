from toolkits.paginate import TableParam
from fastapi import APIRouter, Depends
from ..common import BothAuthParams
from .schema import LogsSchema
from toolkits.influx import Influx
import math

router: APIRouter = APIRouter()



@router.get("/logs", include_in_schema=False)
async def get_logs(logs_schema: LogsSchema = Depends(), table_params: TableParam = Depends(), app = Depends(BothAuthParams)):
    influx_client = Influx()
    results, count = influx_client.logs(logs_schema, table_params)

    nb_pages: int = math.ceil(count/table_params.per_page)
    
    return {
        "data": results,
        "count": count,
        "last_page": nb_pages
    }


@router.get("/chart", include_in_schema=False)
async def get_chart(logs_schema: LogsSchema = Depends(), app = Depends(BothAuthParams)):
    influx_client = Influx()
    tmp_data = influx_client.chart(logs_schema)

    data: list = []
    for tmp in tmp_data:
        data.append((tmp["time"], tmp["count"]))

    return data


@router.get("/measurements", include_in_schema=False)
async def get_measurements(app = Depends(BothAuthParams)):
    influx_client = Influx()
    results = influx_client.get_measurements()
    return results
    