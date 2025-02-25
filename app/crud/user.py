from sqlalchemy.orm import Session
from app.crud.crud_base import CRUDBase
from ..database import models
from ..schemas import user_schemas


class UserCRUD(CRUDBase[models.User, user_schemas.UserCreate, user_schemas.UserUpdate]):
    def __init__(self, model: type[models.User]):
        super().__init__(model)
