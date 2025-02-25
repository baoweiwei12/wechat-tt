from sqlalchemy.orm import Session
from app.crud.crud_base import CRUDBase
from ..database import models
from ..schemas import wechat


class WechatMessageCRUD(
    CRUDBase[
        models.WechatMessage, wechat.WechatMessageCreate, wechat.WechatMessageUpdate
    ]
):
    def __init__(self, model: type[models.WechatMessage]):
        super().__init__(model)


class WechatUserCRUD(
    CRUDBase[models.WechatUser, wechat.WechatMessageCreate, wechat.WechatUserUpdate]
):
    def __init__(self, model: type[models.WechatUser]):
        super().__init__(model)
