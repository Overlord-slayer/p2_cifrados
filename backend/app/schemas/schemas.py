from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
	email: EmailStr = Field(..., description="Valid email address")
	password: str = Field(..., min_length=8, max_length=128, description="Password must be 8-128 characters")
	
	@validator('password')
	def validate_password(cls, v):
		if not re.search(r"[A-Z]", v):
			raise ValueError('Password must contain at least one uppercase letter')
		if not re.search(r"[a-z]", v):
			raise ValueError('Password must contain at least one lowercase letter')
		if not re.search(r"\d", v):
			raise ValueError('Password must contain at least one digit')
		if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
			raise ValueError('Password must contain at least one special character')
		return v

# schemas.py
class SignupResponse(BaseModel):
	email: EmailStr
	message: str
	setup_required: bool = True
	
class TOTPSetupResponse(BaseModel):
	totp_secret: str
	qr_code_base64: str

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
	email: EmailStr = Field(..., description="Valid email address")
	password: str = Field(..., min_length=1, max_length=128, description="User password")
	totp_code: str = Field(..., min_length=6, max_length=6, regex=r"^\d{6}$", description="6-digit TOTP code")
	
	@validator('totp_code')
	def validate_totp_code(cls, v):
		if not v.isdigit():
			raise ValueError('TOTP code must contain only digits')
		return v
