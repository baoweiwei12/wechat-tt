from datetime import datetime, timedelta
from fastapi import HTTPException
import requests
from app.core import security
from app.core.config import CONFIG
from app.database import models
from app.schemas import user_schemas
from app.database.db import main_db
from sqlalchemy.orm import Session
from app.crud.user import UserCRUD
from .verification_code import VerificationCodeService
from app.core.config import GOOGLESettings


class UserService:

    def __init__(self, user_crud: UserCRUD):
        self.user_crud = user_crud

    @staticmethod
    def create_admin():
        """
        创建管理员
        """
        db = main_db.get_db()
        try:
            user_crud = UserCRUD(models.User)
            admin = user_crud.get_by_filter(
                db, user_crud.model.email == "admin@admin.com"
            )
            if admin is None:
                new_admin = user_schemas.UserCreate(
                    username="admin",
                    email="admin@admin.com",
                    nickname="管理员",
                    password="admin123",
                    role="admin",
                    level=3,
                )
                user_crud.create(db, new_admin)
                return True
            return False
        finally:
            db.close()

    def get(self, db: Session, user_id: int):
        db_user = self.user_crud.get(db, user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    def get_by_email(self, db: Session, email: str):
        user = self.user_crud.get_by_filter(db, self.user_crud.model.email == email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_by_username(self, db: Session, username: str):
        user = self.user_crud.get_by_filter(
            db, self.user_crud.model.username == username
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def cheack_username_exists(self, db: Session, username: str):
        user = self.user_crud.get_by_filter(
            db, self.user_crud.model.username == username
        )
        if user:
            raise HTTPException(status_code=400, detail="Username already exists")

    def cheack_email_exists(self, db: Session, email: str):
        user = self.user_crud.get_by_filter(db, self.user_crud.model.email == email)
        if user:
            raise HTTPException(status_code=400, detail="Email already exists")

    def create(self, db: Session, new_user: user_schemas.UserCreate):
        self.cheack_username_exists(db, new_user.username)
        self.cheack_email_exists(db, new_user.email)
        return self.user_crud.create(db, new_user)

    def search(
        self,
        db: Session,
        keyword: str | None = None,
        page: int = 1,
        per_page: int = 100,
    ):
        if keyword is None:
            total, data = self.user_crud.get_multi(db, page, per_page)
        else:
            total, data = self.user_crud.get_multi_by_filter(
                db, self.user_crud.model.username.like(f"%{keyword}%"), page, per_page
            )
        return {"total": total, "data": data}

    def update(self, db: Session, user_id: int, update_data: user_schemas.UserUpdate):
        if update_data.username:
            self.cheack_username_exists(db, update_data.username)
        if update_data.email:
            self.cheack_email_exists(db, update_data.email)
        updated_user = self.user_crud.update(db, user_id, update_data)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user

    def ban(self, db: Session, user_id: int):
        """
        封禁用户
        """
        return self.update(db, user_id, user_schemas.UserUpdate(is_banned=True))

    def _generate_token(self, user: models.User):
        expires_delta = timedelta(minutes=CONFIG.JWT.EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data=security.TokenData(**user.__dict__), expires_delta=expires_delta
        )
        return security.Token(
            access_token=access_token,
            token_type="bearer",
            expire_at=datetime.now() + expires_delta,
        )

    def _authenticate_user(self, user: models.User | None, password: str):
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if (password == str(user.password)) is False:
            raise HTTPException(
                status_code=401,
                detail="Password is incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return self._generate_token(user)

    def login_by_email(self, db: Session, params: user_schemas.UserLoginByEmail):
        user = self.get_by_email(db, params.email)
        return self._authenticate_user(user, params.password)

    def login(self, db: Session, username: str, password: str):
        user = self.get_by_username(db, username)
        return self._authenticate_user(user, password)

    def login_with_code(
        self,
        db: Session,
        params: user_schemas.UserLoginWithCode,
        verification_code_service: VerificationCodeService,
    ):
        verification_code_service.verify_code(db, params.email, params.code)
        user = self.get_by_email(db, params.email)
        expires_delta = timedelta(minutes=CONFIG.JWT.EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data=security.TokenData(**user.__dict__), expires_delta=expires_delta
        )
        return security.Token(
            access_token=access_token,
            token_type="bearer",
            expire_at=datetime.now() + expires_delta,
        )

    def register_user(
        self,
        db: Session,
        user: user_schemas.UserRegister,
        verification_code_service: VerificationCodeService,
    ) -> user_schemas.User:
        verification_code_service.verify_code(db, user.email, user.code)
        return self.create(
            db,
            user_schemas.UserCreate(
                username=user.username,
                email=user.email,
                password=user.password,
                nickname=user.username,
            ),
        )

    def login_with_google(
        self,
        db: Session,
        google_code: str,
        google_config: GOOGLESettings,
        redirect_uri: str | None = None,
    ) -> security.Token:
        response = requests.post(
            google_config.TOKEN_URI,
            data={
                "code": google_code,
                "client_id": google_config.CLIENT_ID,
                "client_secret": google_config.CLIENT_SECRET,
                "redirect_uri": (
                    google_config.REDIRECT_URI if redirect_uri is None else redirect_uri
                ),
                "grant_type": "authorization_code",
            },
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Invalid code or authorization failed"
            )

        token_data = response.json()
        if "access_token" not in token_data:
            raise HTTPException(
                status_code=400, detail="Invalid code or authorization failed"
            )

        access_token = token_data["access_token"]

        # 获取用户信息
        response = requests.get(
            google_config.USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Failed to fetch user information"
            )

        user_info = response.json()

        email = user_info["email"]

        db_user = self.user_crud.get_by_filter(db, self.user_crud.model.email == email)
        if db_user:
            return self._generate_token(db_user)
        else:
            # 创建新用户
            user = self.create(
                db,
                user_schemas.UserCreate(
                    username=user_info["sub"],
                    email=email,
                    password=email,
                    nickname="Google User " + user_info["sub"],
                ),
            )
            return self._generate_token(user)
