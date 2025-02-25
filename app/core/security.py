import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from app.core.config import CONFIG


class TokenData(BaseModel):
    id: int
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expire_at: datetime


def create_access_token(data: TokenData, expires_delta: timedelta | None = None):
    to_encode = data.model_dump().copy()
    expires_delta = expires_delta or timedelta(minutes=CONFIG.JWT.EXPIRE_MINUTES)
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, CONFIG.JWT.SECRET_KEY, algorithm=CONFIG.JWT.ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str, credentials_exception: Exception):
    try:
        payload = jwt.decode(
            token, CONFIG.JWT.SECRET_KEY, algorithms=[CONFIG.JWT.ALGORITHM]
        )
        email: str | None = payload.get("email")
        id: int | None = payload.get("id")
        username: str | None = payload.get("username")
        if email is None or id is None or username is None:
            raise credentials_exception
        return TokenData(email=email, id=id, username=username)
    except jwt.PyJWTError:
        raise credentials_exception


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
