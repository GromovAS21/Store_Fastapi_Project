from fastapi import FastAPI

from routers import auth, permissions, reviews
from routers import products, categories

app = FastAPI()

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permissions.router)
app.include_router(reviews.router)
