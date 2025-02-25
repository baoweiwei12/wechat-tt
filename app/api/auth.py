from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.schemas import user_schemas
from app.service.user import UserService
from app.service.verification_code import VerificationCodeService
from . import _dps
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.core.config import CONFIG
import requests
from typing import Literal

router = APIRouter(tags=["用户鉴权"])

GOOGLE = CONFIG.GOOGLE


# 测试谷歌登录
@router.get("/auth/google", summary="google登录")
def login_google_redirect(redirect_uri: str | None = None):
    authorization_url = f"{GOOGLE.AUTH_URI}?client_id={GOOGLE.CLIENT_ID}&redirect_uri={GOOGLE.REDIRECT_URI if redirect_uri is None else redirect_uri}&response_type=code&scope=openid email"
    return RedirectResponse(authorization_url)


@router.post(
    "/login/google",
    response_model=security.Token,
    summary="google登录 传入redirect_uri 和 code",
)
def login_google(
    code: str,
    redirect_uri: str,
    db: Session = Depends(_dps.get_db),
    user_service: UserService = Depends(_dps.get_user_service),
):
    return user_service.login_with_google(db, code, GOOGLE, redirect_uri)


# @router.get("/login/google/callback", response_model=security.Token)
# def login_google_callback(
#     code: str,
#     db: Session = Depends(_dps.get_db),
#     user_service: UserService = Depends(_dps.get_user_service),
# ):
#     token = user_service.login_with_google(db, code, GOOGLE)
#     app_url = f"http://127.0.0.1:8080/#/google-login?access_token={token.access_token}"
#     print(app_url)
#     return RedirectResponse(app_url)


@router.post("/login/token", response_model=security.Token, summary="用户名密码登录")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(_dps.get_db),
    user_service: UserService = Depends(_dps.get_user_service),
):

    return user_service.login(db, form_data.username, form_data.password)


@router.post(
    "/login/token-with-code", response_model=security.Token, summary="验证码登录"
)
def login_with_code(
    params: user_schemas.UserLoginWithCode,
    db: Session = Depends(_dps.get_db),
    user_service: UserService = Depends(_dps.get_user_service),
    verification_code_service: VerificationCodeService = Depends(
        _dps.get_verification_code_service
    ),
):

    return user_service.login_with_code(db, params, verification_code_service)


@router.get("/verify-code", summary="获取邮箱验证码")
def get_verify_code(
    email: EmailStr = Query(..., description="邮箱"),
    db: Session = Depends(_dps.get_db),
    verification_code_service: VerificationCodeService = Depends(
        _dps.get_verification_code_service
    ),
):

    return verification_code_service.send_code(db, email)


@router.post(
    "/register", response_model=user_schemas.UserInResponse, summary="用户注册"
)
def register_user(
    user: user_schemas.UserRegister,
    db: Session = Depends(_dps.get_db),
    user_service: UserService = Depends(_dps.get_user_service),
    verification_code_service: VerificationCodeService = Depends(
        _dps.get_verification_code_service
    ),
):
    return user_service.register_user(db, user, verification_code_service)
