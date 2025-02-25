from sqlalchemy import (
    JSON,
    TEXT,
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    func,
    DECIMAL,
)
from sqlalchemy.ext.declarative import declarative_base
from .db import main_db

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表，存储系统中的用户信息"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(
        String(100), nullable=False, unique=True, index=True, comment="用户名"
    )
    email = Column(String(100), nullable=False, unique=True, index=True, comment="邮箱")
    password = Column(String(255), nullable=False, comment="密码")
    nickname = Column(String(100), nullable=False, comment="昵称")
    role = Column(String(50), nullable=False, comment="角色 'admin' 'user' ")
    level = Column(Integer, nullable=False, comment="等级 '0-3' ")
    is_banned = Column(Boolean, nullable=False, default=False, comment="是否封禁")
    created_at = Column(
        DateTime, nullable=False, default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )


class VerificationCode(Base):
    __tablename__ = "verification_codes"
    __table_args__ = {"comment": "验证码表，存储用户验证码信息"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="验证码ID")
    email = Column(String(40), nullable=False, comment="邮箱")
    code = Column(String(4), nullable=False, comment="4位数字验证码")
    created_at = Column(
        DateTime, nullable=False, default=func.now(), comment="创建时间"
    )
    is_used = Column(Boolean, nullable=False, default=False, comment="是否已使用")


class WechatUser(Base):
    __tablename__ = "wechat_users"
    __table_args__ = {"comment": "微信用户表，存储微信用户信息"}

    wxid = Column(String(255), primary_key=True, comment="微信用户wxid")
    nickname = Column(String(255), nullable=True, comment="微信用户昵称")
    wechat_id = Column(String(255), nullable=True, comment="微信id")
    remark = Column(String(255), nullable=True, comment="微信备注")
    created_at = Column(
        DateTime, nullable=False, default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    is_deleted = Column(Boolean, nullable=False, default=False, comment="是否已删除")


class WechatMessage(Base):
    __tablename__ = "wechat_message"

    id = Column(BigInteger, primary_key=True)
    is_self = Column(Boolean, nullable=False)
    is_group = Column(Boolean, nullable=False)
    type = Column(Integer, nullable=False)
    ts = Column(BigInteger, nullable=False)
    roomid = Column(String(255), nullable=True)
    content = Column(TEXT, nullable=True)
    sender = Column(String(255), nullable=False)
    sign = Column(String(255), nullable=True)
    thumb = Column(String(255), nullable=True)
    extra = Column(String(255), nullable=True)
    xml = Column(TEXT, nullable=True)


class RoomidChatidDict(Base):
    __tablename__ = "roomid_chatid_dict"
    __table_args__ = {"comment": "roomid_chatid_dict表，存储房间对应会话字典表"}

    roomid = Column(String(255), primary_key=True, comment="roomid")
    chat_id = Column(String(255), nullable=False, comment="chat_id")


# 创建表
Base.metadata.create_all(bind=main_db.engine)
