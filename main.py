from fastapi import FastAPI

from routers import auth, permissions, reviews
from routers import products, categories

app = FastAPI()
app_v1 = FastAPI(
    title="My API v1",
    description="The first version of my API",
)

app_v1.include_router(categories.router)
app_v1.include_router(products.router)
app_v1.include_router(auth.router)
app_v1.include_router(permissions.router)
app_v1.include_router(reviews.router)


app.mount("/v1", app_v1) # Версионирование
