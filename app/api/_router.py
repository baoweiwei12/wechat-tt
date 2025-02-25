from fastapi import APIRouter
from . import auth, user, wechat

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth.router)
v1_router.include_router(user.router)
v1_router.include_router(wechat.router)
