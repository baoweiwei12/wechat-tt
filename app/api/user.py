from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.schemas import user_schemas
from app.database import models
from app.service.verification_code import VerificationCodeService
from . import _dps
from sqlalchemy.orm import Session
from app.service.user import UserService

router = APIRouter(prefix="/users", tags=["用户相关"])


@router.get(
    "/me", response_model=user_schemas.UserInResponse, summary="获取当前用户信息"
)
def read_users_me(currernt_user: models.User = Depends(_dps.get_current_user)):
    return currernt_user


@router.get(
    "/{user_id}",
    response_model=user_schemas.UserInResponse,
    dependencies=[Depends(_dps.check_role(["admin"]))],
    summary="获取用户信息",
)
def read_user(
    user_id: int = Path(..., gt=0),
    db: Session = Depends(_dps.get_db),
    user_service: UserService = Depends(_dps.get_user_service),
):
    return user_service.get(db, user_id)


@router.get(
    "",
    response_model=user_schemas.UsersResponse,
    dependencies=[Depends(_dps.check_role(["admin"]))],
    summary="获取用户列表",
)
def read_users(
    keyword: str | None = Query(default=None, description="搜索关键字", max_length=20),
    page: int = Query(1, description="页码", ge=1),
    per_page: int = Query(10, description="每页条数", ge=1, le=100),
    db: Session = Depends(_dps.get_db),
    user_service: UserService = Depends(_dps.get_user_service),
):

    return user_service.search(db, keyword, page, per_page)


@router.post(
    "/me/password",
    response_model=user_schemas.UserInResponse,
    summary="修改当前用户密码",
)
def update_my_password(
    req: user_schemas.UserChangePassword,
    db: Session = Depends(_dps.get_db),
    current_user: user_schemas.User = Depends(_dps.get_current_user),
    user_service: UserService = Depends(_dps.get_user_service),
):
    if req.old_password != current_user.password:
        raise HTTPException(status_code=400, detail="Old password is incorrect.")
    if req.old_password == req.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as old password."
        )
    return user_service.update(
        db, current_user.id, user_schemas.UserUpdate(password=req.new_password)
    )
