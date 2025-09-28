from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
	email: EmailStr
	password: str = Field(..., min_length=8, max_length=128, description="Password must be 8-128 characters")
	
	@validator('password')
	def validate_password(cls, v):
		if len(v) < 8:
			raise ValueError('Password must be at least 8 characters long')
		if not re.search(r'[A-Z]', v):
			raise ValueError('Password must contain at least one uppercase letter')
		if not re.search(r'[a-z]', v):
			raise ValueError('Password must contain at least one lowercase letter')
		if not re.search(r'[0-9]', v):
			raise ValueError('Password must contain at least one digit')
		if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
			raise ValueError('Password must contain at least one special character')
		return v
	
	@validator('email')
	def validate_email(cls, v):
		# Additional email validation beyond EmailStr
		if len(v) > 254:  # RFC 5321 limit
			raise ValueError('Email address too long')
		return v.lower()  # Normalize email to lowercase

# schemas.py
class SignupResponse(BaseModel):
	email: EmailStr
	message: str
	setup_required: bool

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
	password: str = Field(..., min_length=1, max_length=128)
	totp_code: str = Field(..., min_length=6, max_length=6, regex=r'^\d{6}$')
	
	@validator('email')
	def validate_email_login(cls, v):
		if len(v) > 254:  # RFC 5321 limit
			raise ValueError('Email address too long')
		return v.lower()  # Normalize email to lowercase
	
	@validator('totp_code')
	def validate_totp_code(cls, v):
		if not v.isdigit():
			raise ValueError('TOTP code must contain only digits')
		if len(v) != 6:
			raise ValueError('TOTP code must be exactly 6 digits')
		return v
