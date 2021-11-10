import uvicorn
from config import settings
from mongoengine import connect
from apps.auth.models import User
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from apps.auth.tools import get_current_user
from starlette.middleware import Middleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from mongoengine.connection import disconnect
from toolkits.rabbitmq.realtime import RealTime
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi_contrib.exception_handlers import setup_exception_handlers

from apps.auth.routers import router as auth_router
from apps.auth.user_router import router as user_router
from apps.config.routers import router as config_router
from apps.input.routers import router as input_router
from apps.metrics.routers import router as metrics_router
from apps.rule.routers import router as rule_router
from apps.agent.routers import router as agent_router
from apps.dashboards.routers import router as dashboard_router
from apps.alert.routers import router as alert_router

templates = Jinja2Templates(directory="templates")

middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_headers=["*"],
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT"],
    )
]

app = FastAPI(
    debug=settings.DEBUG,
    middleware=middlewares,
    title="LightOwl",
)

real_time = RealTime()

if not settings.DEBUG:
    app.mount("/static", StaticFiles(directory="templates/static"), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def main(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
async def startup() -> None:
    params = {
        "host": settings.MONGO_URL,
        "alias": "default"
    }

    connect(settings.MONGO_DATABASE, **params)
    await real_time.setup("alerting")
    # setup_exception_handlers(app)

@app.on_event("shutdown")
async def shutdown_db_client():
    disconnect(alias="default")


app.include_router(auth_router, tags=["Auth"], prefix="/api/v1/auth")
app.include_router(dashboard_router, tags=["Dashboard"], prefix="/api/v1/dashboard")
app.include_router(rule_router, tags=["Rules"], prefix="/api/v1/rules")
app.include_router(config_router, tags=["Config"], prefix="/api/v1/config")
app.include_router(user_router, tags=["Users"], prefix="/api/v1/users")
app.include_router(input_router, tags=['Inputs'], prefix="/api/v1/inputs")
app.include_router(metrics_router, tags=['Metrics'], prefix="/api/v1/metrics")
app.include_router(agent_router, tags=["Agents"], prefix="/api/v1/agents")
app.include_router(alert_router, tags=["Alerts"], prefix="/api/v1/alerts")


@app.websocket("/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await real_time.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            current_user: User = await get_current_user(data)
            if not current_user:
                real_time.remove(websocket)
                break

    except WebSocketDisconnect:
        real_time.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
