from sqlalchemy.orm import Session
from app.crud.crud_base import CRUDBase
from ..database import models
from ..schemas import verification_code_schemas


class VerificationCodeCRUD(
    CRUDBase[
        models.VerificationCode,
        verification_code_schemas.VerificationCodeCreate,
        verification_code_schemas.VerificationCodeUpdate,
    ]
):
    def __init__(self, model: type[models.VerificationCode]):
        super().__init__(model)
