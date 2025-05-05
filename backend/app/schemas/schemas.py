from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

# schemas.py
class SignupResponse(BaseModel):
    email: EmailStr
    totp_secret: str
    qr_code_base64: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = {
        "from_attributes": True  # <- Nuevo en Pydantic v2
    }

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    email: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    totp_code: str
