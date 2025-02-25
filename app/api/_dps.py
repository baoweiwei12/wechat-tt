from typing import List, Literal
from PyPDF2 import PdfReader
import docx2txt
from app.crud.roomid_chatid_dict import RoomidChatidDictCRUD
from app.crud.wechat import WechatMessageCRUD, WechatUserCRUD
from app.database.db import main_db
from app.database import models
from fastapi import Body, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_access_token
from sqlalchemy.orm import Session
from app.service.gingai import GingAIClient, GingAIOptions
from app.service.user import UserService
from app.service.verification_code import VerificationCodeService
from app.crud.user import UserCRUD
from app.crud.verification_code import VerificationCodeCRUD
from langchain_community.utilities import BingSearchAPIWrapper
from app.core.config import CONFIG
from app.service.wcf import WcfClient
from app.schemas.wechat import WechatMessage
from app.service.wechat import WechatService


def get_db():
    db = main_db.get_db()
    try:
        yield db
    finally:
        db.close()


def get_user_crud():
    return UserCRUD(models.User)


def get_verification_code_crud():
    return VerificationCodeCRUD(models.VerificationCode)


def get_user_service(user_crud: UserCRUD = Depends(get_user_crud)):
    return UserService(user_crud)


def get_verification_code_service(
    verification_code_crud: VerificationCodeCRUD = Depends(get_verification_code_crud),
):
    return VerificationCodeService(verification_code_crud)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="v1/login/token")),
    user_service: UserService = Depends(get_user_service),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token 无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = user_service.get(db, token_data.id)
    if user is None:
        raise credentials_exception
    return user


def check_role(required_roles: List[Literal["admin", "user"]]):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问",
            )
        return current_user

    return role_checker


def file_to_text(file: UploadFile = File(...)) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    if file.size is None or file.size > (1 * 1024 * 1024):  # 1 MB
        raise HTTPException(status_code=413, detail="File size exceeds 1MB limit.")

    ext = file.filename.split(".")[-1].lower()
    try:
        if ext == "pdf":
            pdf_reader = PdfReader(file.file)
            text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        elif ext in ["doc", "docx"]:
            text = docx2txt.process(file.file)
        elif ext in ["md", "txt"]:
            content = file.file.read()
            if not content.strip():
                raise ValueError("The file is empty.")
            text = content.decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: .{ext}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {e}")

    if not text.strip():
        raise HTTPException(
            status_code=400, detail="The file is empty or contains no readable text."
        )

    return text.strip()


def get_bing_search_wrapper():
    return BingSearchAPIWrapper(
        bing_subscription_key=CONFIG.BING.API_KEY,
        bing_search_url=CONFIG.BING.SEARCH_URL,
    )


def get_wcf_client():
    return WcfClient(CONFIG.WCF.API_BASE)


def receive_wechat_message(wechat_message: WechatMessage = Body(...)):
    return wechat_message


def get_wechat_message_crud():
    return WechatMessageCRUD(models.WechatMessage)


def get_wechat_user_crud():
    return WechatUserCRUD(models.WechatUser)


def get_roomid_chatid_dict_crud():
    return RoomidChatidDictCRUD(models.RoomidChatidDict)


def get_gingai_client(options: GingAIOptions | Literal["default"] = "default"):
    def gingai_client_factory():
        if options == "default":
            return GingAIClient(
                api_base=CONFIG.GINGAI.API_BASE,
                api_key=CONFIG.GINGAI.API_KEY,
                application_id=CONFIG.GINGAI.APP_ID,
            )
        else:
            return GingAIClient(
                api_base=options.api_base,
                api_key=options.api_key,
                application_id=options.application_id,
            )

    return gingai_client_factory


def get_wechat_service(
    wechat_message_crud: WechatMessageCRUD = Depends(get_wechat_message_crud),
    wechat_user_crud: WechatUserCRUD = Depends(get_wechat_user_crud),
    wcf_client: WcfClient = Depends(get_wcf_client),
    gingai_client: GingAIClient = Depends(get_gingai_client("default")),
    roomid_chatid_dict_crud: RoomidChatidDictCRUD = Depends(
        get_roomid_chatid_dict_crud
    ),
):
    return WechatService(
        wechat_user_crud,
        wechat_message_crud,
        wcf_client,
        gingai_client,
        roomid_chatid_dict_crud,
    )
