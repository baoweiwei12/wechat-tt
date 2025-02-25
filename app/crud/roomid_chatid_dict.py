from sqlalchemy.orm import Session
from app.crud.crud_base import CRUDBase
from ..database import models
from ..schemas import roomid_chatid_dict


class RoomidChatidDictCRUD(
    CRUDBase[
        models.RoomidChatidDict,
        roomid_chatid_dict.RoomidChatidDictCreate,
        roomid_chatid_dict.RoomidChatidDictUpdate,
    ]
):
    def __init__(self, model: type[models.User]):
        super().__init__(model)
