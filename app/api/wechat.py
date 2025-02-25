from pprint import pprint
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.schemas import user_schemas, wechat
from app.database import models
from app.service.verification_code import VerificationCodeService
from app.service.wechat import WechatService
from . import _dps
from sqlalchemy.orm import Session
from app.service.user import UserService
from app.service.wcf import WcfClient
import logging
from app.service.gingai import GingAIClient

router = APIRouter(prefix="/wechat", tags=["wechat"])


@router.post("/webhook", summary="微信webhook")
def webhook(
    message: wechat.WechatMessage = Depends(_dps.receive_wechat_message),
    wechat_service: WechatService = Depends(_dps.get_wechat_service),
    db: Session = Depends(_dps.get_db),
):
    logging.info(f"receive wechat message: {message.model_dump(exclude={'xml'})}")
    wechat_service.save_message(db, wechat.WechatMessageCreate(**message.model_dump()))
    wechat_service.bot_reply_process(db, message)
    return {"message": "ok"}
