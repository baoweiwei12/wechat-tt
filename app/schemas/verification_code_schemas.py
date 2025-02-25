from pydantic import BaseModel


class VerificationCodeCreate(BaseModel):
    email: str
    code: str
    is_used: bool = False


class VerificationCodeUpdate(BaseModel):
    is_used: bool


class VerificationCode(VerificationCodeCreate):
    id: int
    created_at: str

    class Config:
        from_attribute = True
