from typing import Any, Dict
from pydantic import BaseModel
import yaml


class MYSQLSettings(BaseModel):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    DATABASE: str


class JWTSettings(BaseModel):
    SECRET_KEY: str
    ALGORITHM: str
    EXPIRE_MINUTES: int


class AppSettings(BaseModel):
    NAME: str
    VERSION: str
    DESCRIPTION: str


class EmailSettings(BaseModel):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    FROM: str


class BingSettings(BaseModel):
    API_KEY: str
    SEARCH_URL: str


class GOOGLESettings(BaseModel):
    CLIENT_ID: str
    PROJECT_ID: str
    AUTH_URI: str
    TOKEN_URI: str
    AUTH_PROVIDER_X509_CERT_URL: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    USERINFO_URL: str


class WCFSettings(BaseModel):
    API_BASE: str


class GingAISettings(BaseModel):
    API_BASE: str
    API_KEY: str
    APP_ID: str


class AppConfig(BaseModel):
    APP: AppSettings
    MYSQL: MYSQLSettings
    JWT: JWTSettings
    EMAIL: EmailSettings
    BING: BingSettings
    GOOGLE: GOOGLESettings
    WCF: WCFSettings
    GINGAI: GingAISettings

    @classmethod
    def from_yaml(cls, file_path: str):
        with open(file_path, "r") as file:
            config_data: Dict[str, Any] = yaml.safe_load(file)
        return cls(**config_data)


CONFIG = AppConfig.from_yaml("config.yaml")
