from .schema import (DashboardSchema, ExecuteQuerySchema, HomeSchema, WidgetDashboardSchema, DashboardCreateSchema)
from .models import Dashboard, DashboardWidgets, GeneralDashboard, Widget
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from toolkits.paginate import TableParam
from starlette.responses import Response
from .toolkits.widget import WidgetData
from ..common import BothAuthParams
from fastapi import APIRouter, status
from apps.agent.models import Agent
from typing import List, Union

router: APIRouter = APIRouter()


@router.get("/home", response_model=List[HomeSchema])
async def home(pagination: TableParam = Depends(), app = Depends(BothAuthParams)):
    sort_field, order = pagination.sort.split("|")

    order_dir: dict = {
        "descending": 1,
        "ascending": 1,
        "desc": -1,
        "asc": -1
    }

    query: dict = {}
    lookup: dict = {
        "from": "alert",
        "localField": "_id",
        "foreignField": "agent",
        "as": "alerts"
    }


    aggs = [
        {"$match": query},
        {"$sort": { sort_field: order_dir.get(order, -1)}},
        {"$lookup": lookup}
    ]

    data_tmp = Agent.objects.aggregate(*aggs)

    to_return: list = []
    for tmp in data_tmp:
        to_return.append(HomeSchema(**tmp))

    return to_return


@router.get("/", response_model=List[DashboardSchema])
async def get_dashboards(agent_id: str, app = Depends(BothAuthParams)):
    agent = Agent.objects(pk=agent_id).get()
    dashboards: list = Dashboard.objects(agent=agent)
    return dashboards


@router.get("/{id}", response_model=DashboardSchema)
async def get_dashboard(id: str, app = Depends(BothAuthParams)):
    try:
        dashboard = Dashboard.objects(pk=id).get()
        widgets = DashboardWidgets.objects(dashboard=dashboard)

        schema = DashboardSchema(**dashboard.to_mongo())
        schema.widgets = [WidgetDashboardSchema(**widget.to_mongo()) for widget in widgets]
        return schema

    except (Dashboard.DoesNotExist, GeneralDashboard.DoesNotExist):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/query")
async def execute_query(params: Union[List[ExecuteQuerySchema], ExecuteQuerySchema], app = Depends(BothAuthParams)):
    widget: WidgetData = WidgetData(params)
    return widget.fetch_influxdata()


# @router.get("/widget/{id}", response_model=WidgetSchema)
# async def get_widget(id: str, app = Depends(BothAuthParams)):
#     try:
#         widget = Widget.objects(pk=id).get()
#         return WidgetSchema(**widget.to_mongo())
#     except Widget.DoesNotExist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# @router.put("/widget/{id}", status_code=status.HTTP_204_NO_CONTENT)
# async def edit_widget(id: str, widget_schema: WidgetCreateSchema, app = Depends(BothAuthParams)):
#     try:
#         widget = Widget.objects(pk=id).get()
#         widget.name = widget_schema.name
#         widget.graph_type = widget_schema.graph_type
#         widget.query = widget_schema.query
#         widget.options = widget_schema.options
#         widget.interval = widget_schema.interval
#         widget.save()
#     except Widget.DoesNotExist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# @router.delete("/widget/{id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_widget(id: str, app = Depends(BothAuthParams)):
#     try:
#         widget = Widget.objects(pk=id).get()
#         widget.delete()
#     except Widget.DoesNotExist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_dashboard(dashboard_schema: DashboardCreateSchema, app = Depends(BothAuthParams)):
    try:
        dashboard = Dashboard(**dashboard_schema.dict())

        if not Dashboard.objects.count():
            dashboard.general = True
        
        dashboard.save()

        for widget in dashboard_schema.widgets:
            widget = widget.dict()
            widget["dashboard"] = dashboard
            widget["widget"] = Widget.objects(pk=widget["widget_id"]).get()
            dashboard_widget = DashboardWidgets(**widget)
            dashboard_widget.save()
        
        return DashboardSchema(**dashboard.to_mongo())
    except Exception as error:
        raise


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_dashboard(id: str, dashboard_schema: DashboardCreateSchema, app = Depends(BothAuthParams)):
    try:
        dashboard = Dashboard.objects(pk=id).get()

        DashboardWidgets.objects(dashboard=dashboard).delete()
        dashboard.name = dashboard_schema.name
        for widget in dashboard_schema.widgets:
            widget = widget.dict()
            widget["dashboard"] = dashboard
            widget["widget"] = Widget.objects(pk=widget["widget_id"]).get()
            dashboard_widget = DashboardWidgets(**widget)
            dashboard_widget.save()
        
        dashboard.save()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Dashboard.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
