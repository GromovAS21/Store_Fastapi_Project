from celery import Celery
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect

from middleware import TimingMiddleware, log_middleware
from routers import auth, permissions, reviews, tests, websockets
from routers import products, categories
from websocket import ConnectionManager

app = FastAPI()
app_v1 = FastAPI(
    title="My API v1",
    description="The first version of my API",
)

templates = Jinja2Templates(directory="templates")

logger.add("info.log", format="Log: [{time} - {level} - {message}]", level="INFO", enqueue = True)


origins = [
    "http://127.0.0.1:8000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TimingMiddleware)
app.middleware("http")(log_middleware)

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
    broker_connection_retry_on_startup=True
)

celery.conf.beat_schedule = {
    "run-me-background-task": {
        "task": "tasks.call_background_task",
        "schedule": 60.0,
        "args": ("Test text message",)
    }
}
app_v1.include_router(categories.router)
app_v1.include_router(products.router)
app_v1.include_router(auth.router)
app_v1.include_router(permissions.router)
app_v1.include_router(reviews.router)
app_v1.include_router(tests.router)
app.include_router(websockets.router)

app.mount("/v1", app_v1)  # Версионирование


@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

