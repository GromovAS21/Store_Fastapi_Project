from celery import Celery
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

import tasks
from middleware import TimingMiddleware, log_middleware
from routers import auth, permissions, reviews, tests
from routers import products, categories

app = FastAPI()
app_v1 = FastAPI(
    title="My API v1",
    description="The first version of my API",
)

logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}]", level="INFO", enqueue = True)


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

app.mount("/v1", app_v1)  # Версионирование





