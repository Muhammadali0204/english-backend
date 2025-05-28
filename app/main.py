from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tortoise.contrib.fastapi import register_tortoise

from app.routers.main import router
from app.core.config import DATABASE_CONFIG


app = FastAPI(openapi_version="3.1.0", redirect_slashes=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(app, config=DATABASE_CONFIG, generate_schemas=True)

app.include_router(router)
