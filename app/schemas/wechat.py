from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class MessageType(Enum):
    FRIEND_CIRCLE = 0
    TEXT = 1
    IMAGE = 3
    VOICE = 34
    FRIEND_CONFIRMATION = 37
    POSSIBLE_FRIEND_MSG = 40
    BUSINESS_CARD = 42
    VIDEO = 43
    EMOJI_GAME = 47
    LOCATION = 48
    SHARED_LOCATION_FILE_TRANSFER_LINK = 49
    VOIP_MSG = 50
    WECHAT_INIT = 51
    VOIP_NOTIFY = 52
    VOIP_INVITE = 53
    SHORT_VIDEO = 62
    WECHAT_REDPACKET = 66
    SYS_NOTICE = 9999
    SYSTEM_MESSAGE = 10000
    REVOKE_MESSAGE = 10002
    SOGOU_EMOJI = 1048625
    LINK = 16777265
    WECHAT_REDPACKET_V2 = 436207665
    REDPACKET_COVER = 536936497
    VIDEO_CHANNEL_VIDEO = 754974769
    VIDEO_CHANNEL_CARD = 771751985
    QUOTED_MESSAGE = 822083633
    TAP_TAP = 922746929
    VIDEO_CHANNEL_LIVE = 973078577
    PRODUCT_LINK = 974127153
    VIDEO_CHANNEL_LIVE_V2 = 975175729
    MUSIC_LINK = 1040187441
    FILE = 1090519089


class WechatMessage(BaseModel):
    is_self: bool
    is_group: bool
    id: int
    type: MessageType
    ts: int
    roomid: str
    content: str
    sender: str
    sign: str
    thumb: str
    extra: str
    xml: str


class WechatMessageCreate(WechatMessage):
    type: int

    @classmethod
    def from_wechat_message(cls, message: "WechatMessage"):
        """转换 `WechatMessage` 为 `WechatMessageCreate`，自动转换 `type`"""
        return cls(**message.model_dump(), type=message.type.value)


class WechatMessageUpdate(WechatMessage):
    pass


class WechatUserCreate(BaseModel):
    wxid: str
    nickname: str
    wechat_id: str
    remark: str
    is_deleted: bool = False


class WechatUserUpdate(BaseModel):
    is_deleted: bool | None = None


class WechatUser(WechatUserCreate):
    ccreated_at: datetime
    updated_at: datetime

    class Config:
        from_attribute = True
