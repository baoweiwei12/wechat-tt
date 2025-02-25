from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Sequence
from datetime import datetime


class UserRegister(BaseModel):
    username: str = Field(max_length=50, description="用户名")
    email: EmailStr = Field(description="邮箱")
    code: str = Field(description="验证码")
    password: str = Field(max_length=50, min_length=6, description="密码")


class UserLoginWithCode(BaseModel):
    email: EmailStr = Field(description="邮箱")
    code: str = Field(description="验证码")


class UserCreate(BaseModel):
    username: str = Field(max_length=50, description="用户名")
    email: EmailStr = Field(description="邮箱")
    password: str = Field(max_length=50, min_length=6, description="密码")
    nickname: str = Field(max_length=50, description="昵称")
    role: Literal["admin", "user"] = Field(default="user", description="用户角色")
    level: int = Field(default=0, ge=0, le=3, description="用户等级")


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=50, description="用户名")
    email: EmailStr | None = Field(default=None, description="邮箱")
    password: str | None = Field(
        default=None, max_length=50, min_length=6, description="密码"
    )
    nickname: str | None = Field(default=None, max_length=50, description="昵称")
    role: Literal["admin", "user"] | None = Field(default=None, description="用户角色")
    level: int | None = Field(default=None, ge=0, le=3, description="用户等级")
    is_banned: bool | None = Field(default=None, description="是否封禁")


class User(UserCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attribute = True


class UserLoginByEmail(BaseModel):
    email: EmailStr = Field(description="邮箱")
    password: str = Field(max_length=50, min_length=6, description="密码")


class UserInResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    username: str = Field(max_length=50, description="用户名")
    email: EmailStr = Field(description="邮箱")
    nickname: str = Field(max_length=50, description="昵称")
    role: Literal["admin", "user"] = Field(default="user", description="用户角色")
    level: int = Field(default=0, ge=0, le=3, description="用户等级")
    is_banned: bool | None = Field(default=None, description="是否封禁")


class UsersResponse(BaseModel):
    data: Sequence[UserInResponse]
    total: int


class UserChangePassword(BaseModel):
    old_password: str = Field(max_length=50, min_length=6, description="旧密码")
    new_password: str = Field(max_length=50, min_length=6, description="新密码")
