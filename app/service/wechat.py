from typing import Callable
from app.crud.wechat import WechatMessageCRUD, WechatUserCRUD
from app.crud.roomid_chatid_dict import RoomidChatidDictCRUD
from app.schemas.roomid_chatid_dict import RoomidChatidDictCreate
from app.schemas.wechat import MessageType, WechatMessage, WechatMessageCreate
from .wcf import WcfClient
from sqlalchemy.orm import Session
import logging
from .gingai import GingAIClient

looger = logging.getLogger(__name__)


class WechatService:

    def __init__(
        self,
        wechat_user_crud: WechatUserCRUD,
        wechat_message_crud: WechatMessageCRUD,
        wcf_client: WcfClient,
        gingai_client: GingAIClient,
        roomid_chatid_dict_crud: RoomidChatidDictCRUD,
    ):

        self.wechat_user_crud = wechat_user_crud
        self.wechat_message_crud = wechat_message_crud
        self.wcf_client = wcf_client
        self.gingai = gingai_client
        self.roomid_chatid_dict_crud = roomid_chatid_dict_crud
        self.process_message_handlers: dict[
            MessageType, Callable[[Session, WechatMessage], None]
        ] = {}
        self.process_message_handlers[MessageType.TEXT] = self._handle_text_message

    def save_message(self, db: Session, message: WechatMessageCreate) -> WechatMessage:
        return self.wechat_message_crud.create(db, message)

    def bot_reply_process(self, db: Session, message: WechatMessage):
        handler_func = self.process_message_handlers.get(message.type)
        if handler_func:
            handler_func(db, message)
        else:
            logging.warning(f"No support message type: {message.type}")

    def is_at_bot(self, message: WechatMessage) -> bool:
        botname = self.wcf_client.get_userinfo()["name"]
        return message.content.startswith(f"@{botname}")

    def _handle_text_message(self, db: Session, message: WechatMessage):
        # 测试如果包含关键字 testreply
        if "testreply" in message.content:
            self.wcf_client.send_text(
                "test reply",
                message.roomid,
                aters=message.sender,
            )
        if message.is_group and self.is_at_bot(message):
            # 获取chatid
            roomid_chatid_dict = self.roomid_chatid_dict_crud.get_by_filter(
                db,
                self.roomid_chatid_dict_crud.model.roomid == message.roomid,
            )
            if roomid_chatid_dict is None:
                chat_id = self.gingai.get_chat_id()
                self.roomid_chatid_dict_crud.create(
                    db,
                    RoomidChatidDictCreate(
                        chat_id=chat_id,
                        roomid=message.roomid,
                    ),
                )
            else:
                chat_id = str(roomid_chatid_dict.chat_id)
            chat_resp = self.gingai.chat(chat_id, message.content)

            self.wcf_client.send_text(
                chat_resp["data"]["content"],
                message.roomid,
                aters=message.sender,
            )
        else:
            pass
