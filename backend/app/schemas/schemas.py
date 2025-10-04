from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
	email: EmailStr
	password: str

# schemas.py - Antienumeración: respuesta uniforme para signup
class SignupResponse(BaseModel):
	detail: str
	created: bool
	# Datos sensibles solo si created=True (se manejan aparte internamente)
	email: EmailStr | None = None
	totp_secret: str | None = None
	qr_code_base64: str | None = None

class UserOut(BaseModel):
	id: int
	email: EmailStr
	is_active: bool

	model_config = {"from_attributes": True}  # <- Nuevo en Pydantic v2

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
