from datetime import datetime, timedelta
from fastapi import HTTPException
from app.core.config import CONFIG
from app.core.email import EmailVerification
from app.crud.verification_code import VerificationCodeCRUD
from app.schemas import verification_code_schemas
from sqlalchemy.orm import Session
from sqlalchemy import and_


class VerificationCodeService:

    def __init__(self, verification_code_crud: VerificationCodeCRUD):
        self.verification_code_crud = verification_code_crud

    def send_code(self, db: Session, email: str):
        # 检查该邮箱1分钟内是否发送过验证码
        db_code = self.verification_code_crud.get_by_filter(
            db, self.verification_code_crud.model.email == email
        )
        if db_code and db_code.created_at > datetime.now() - timedelta(minutes=1):  # type: ignore
            raise HTTPException(
                status_code=400,
                detail="Please wait for 1 minute before sending another verification code.",
            )
        verification = EmailVerification(
            CONFIG.EMAIL.HOST,
            CONFIG.EMAIL.PORT,
            CONFIG.EMAIL.USER,
            CONFIG.EMAIL.PASSWORD,
        )

        new_code = verification.generate_verification_code()
        self.verification_code_crud.create(
            db,
            verification_code_schemas.VerificationCodeCreate(
                email=email, code=new_code
            ),
        )
        if verification.send_verification_email(email):
            return {"message": "ok"}
        raise HTTPException(status_code=500, detail="Error in sending email")

    def verify_code(self, db: Session, email: str, code: str):
        code = self.verification_code_crud.get_by_filter(
            db,
            and_(
                self.verification_code_crud.model.email == email,
                self.verification_code_crud.model.code == code,
                self.verification_code_crud.model.is_used == False,
                self.verification_code_crud.model.created_at
                > datetime.now() - timedelta(minutes=5),  # 验证码有效时间 5分钟
            ),
        )
        if code is None:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        self.verification_code_crud.update(db, code.id, verification_code_schemas.VerificationCodeUpdate(is_used=True))  # type: ignore
