from pydantic import BaseModel


class RoomidChatidDictCreate(BaseModel):
    chat_id: str
    roomid: str


class RoomidChatidDictUpdate(BaseModel):
    chat_id: str | None = None
    roomid: str | None = None


class RoomidChatidDict(RoomidChatidDictCreate):
    class config:
        from_attribute = True
