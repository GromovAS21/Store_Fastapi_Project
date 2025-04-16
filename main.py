import time

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from middleware import TimingMiddleware, log_middleware
from routers import auth, permissions, reviews
from routers import products, categories

app = FastAPI()
app_v1 = FastAPI(
    title="My API v1",
    description="The first version of my API",
)

origins = [
    "http://127.0.0.1:8000/",
]

logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}]", level="INFO", enqueue = True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TimingMiddleware)
app.middleware("http")(log_middleware)

app_v1.include_router(categories.router)
app_v1.include_router(products.router)
app_v1.include_router(auth.router)
app_v1.include_router(permissions.router)
app_v1.include_router(reviews.router)

app.mount("/v1", app_v1)  # Версионирование

def call_background_task(message):
    time.sleep(10)
    print(message)


@app_v1.get("/")
async def hello_world(message: str, background_task: BackgroundTasks):
    background_task.add_task(call_background_task, message)
    return {'message': 'Hello World!'}





