from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from app.core.config import CONFIG
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api._router import v1_router
from .core.log import init_logger
import logging
from app.service.user import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    UserService.create_admin()
    logging.info("Starting up OK")
    yield


app = FastAPI(
    title=CONFIG.APP.NAME,
    description=CONFIG.APP.DESCRIPTION,
    version=CONFIG.APP.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
