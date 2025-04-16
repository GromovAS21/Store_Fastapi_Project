from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware import TimingMiddleware
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TimingMiddleware)

app_v1.include_router(categories.router)
app_v1.include_router(products.router)
app_v1.include_router(auth.router)
app_v1.include_router(permissions.router)
app_v1.include_router(reviews.router)

app.mount("/v1", app_v1)  # Версионирование


@app.get("/")
async def main():
    return {"message": "Hello World"}
