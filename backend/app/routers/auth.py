import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import Header
from sqlalchemy.orm import Session
from app.schemas.schemas import UserCreate, UserOut, Token, UserLogin, SignupResponse
from app.model.models import User
from app.db.db import get_db
from app.auth.utils import verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.totp import verify_totp_token
from app.auth.dependencies import get_current_user
from app.middleware.security import (
    rate_limit_auth_endpoints, 
    account_lockout, 
    add_security_headers
)
import pyotp
import qrcode
import io
import base64

from app.crypto.crypto import *

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=SignupResponse)
async def signup(request: Request, user: UserCreate, db: Session = Depends(get_db)):
	# Apply rate limiting for signup attempts
	await rate_limit_auth_endpoints(request, "signup")
	
	if not user.email or not user.password:
		raise HTTPException(status_code=400, detail="Invalid input data")

	# Verifica si el correo ya está registrado
	db_user = db.query(User).filter(User.email == user.email).first()
	if db_user:
		# Return same response pattern to prevent user enumeration
		raise HTTPException(status_code=400, detail="Registration failed. Please try again.")

	try:
		hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
		totp_secret = pyotp.random_base32()

		private_key, public_key = generate_rsa_keys()
		private_key_encrypted = encrypt_bytes(private_key)

		# Create SQLAlchemy user object
		new_user = User(
			email=user.email,
			hashed_password=hashed_pw,
			totp_secret=totp_secret,
			public_key=bytes_to_str(public_key),
			private_key=bytes_to_str(private_key_encrypted)
		)
		db.add(new_user)
		db.commit()
		db.refresh(new_user)

		# Store TOTP setup completion flag
		# Don't return QR code directly - use separate secure endpoint
		return {
			"email": new_user.email,
			"message": "Registration successful. Use the separate QR endpoint to get your 2FA setup code.",
			"setup_required": True,
		}
	except Exception as e:
		# Log detailed error internally, return generic message
		print(f"Signup error for {user.email}: {str(e)}")  # In production, use proper logging
		raise HTTPException(status_code=400, detail="Registration failed. Please try again.")

@router.post("/login", response_model=Token)
async def signin(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
	# Apply rate limiting for login attempts
	await rate_limit_auth_endpoints(request, "login")
	
	# Check if account is locked due to too many failed attempts
	if account_lockout.is_account_locked(login_data.email):
		raise HTTPException(status_code=429, detail="Account temporarily locked. Please try again later.")
	
	try:
		user = db.query(User).filter_by(email=login_data.email).first()
		
		# Always validate both password and TOTP to prevent timing attacks
		# and user enumeration through response differences
		password_valid = user and verify_password(login_data.password, user.hashed_password)
		totp_valid = user and verify_totp_token(user.totp_secret, login_data.totp_code)
		
		if not password_valid or not totp_valid:
			# Record failed attempt for account lockout
			account_lockout.record_failed_attempt(login_data.email)
			# Generic error message to prevent user enumeration
			raise HTTPException(status_code=401, detail="Invalid credentials or authentication code")

		# Record successful login to clear failed attempts
		account_lockout.record_successful_login(login_data.email)
		
		# Crear tokens
		access_token = create_access_token({"sub": user.email}, scope="user")
		refresh_token = create_refresh_token({"sub": user.email})

		return {
			"access_token": access_token,
			"refresh_token": refresh_token,
			"token_type": "bearer",
		}
	except HTTPException:
		raise
	except Exception as e:
		# Log detailed error internally, return generic message
		print(f"Login error for {login_data.email}: {str(e)}")  # In production, use proper logging
		# Record failed attempt on exception as well
		account_lockout.record_failed_attempt(login_data.email)
		raise HTTPException(status_code=401, detail="Invalid credentials or authentication code")

@router.post("/refresh", response_model=Token)
def refresh_token_endpoint(
	refresh_token: str = Header(...), db: Session = Depends(get_db)
):
	"""
	Recibe un refresh token válido en el header y devuelve nuevos tokens de acceso y refresh.

	Headers:
			refresh_token: str

	Returns:
			dict: Nuevos access_token y refresh_token
	"""
	try:
		payload = decode_token(refresh_token, expected_type="refresh")
		if not payload:
			raise HTTPException(status_code=401, detail="Authentication failed")

		email = payload.get("sub")
		user = db.query(User).filter_by(email=email).first()
		if not user:
			raise HTTPException(status_code=401, detail="Authentication failed")

		new_access_token = create_access_token({"sub": email}, scope="user")
		new_refresh_token = create_refresh_token({"sub": email})

		return {
			"access_token": new_access_token,
			"refresh_token": new_refresh_token,
			"token_type": "bearer",
		}
	except HTTPException:
		raise
	except Exception as e:
		# Log detailed error internally, return generic message
		print(f"Token refresh error for token: {str(e)}")  # In production, use proper logging
		raise HTTPException(status_code=401, detail="Authentication failed")

@router.get("/setup-qr")
def get_setup_qr(
	current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
	"""
	Secure endpoint to get QR code for TOTP setup.
	Requires authentication and only returns QR for the authenticated user.
	"""
	user = db.query(User).filter_by(email=current_user).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	
	try:
		# Generate QR code for authenticated user
		uri = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(
			name=user.email, issuer_name="ChatSecureApp"
		)
		qr_img = qrcode.make(uri)
		buf = io.BytesIO()
		qr_img.save(buf, format="PNG")
		qr_base64 = base64.b64encode(buf.getvalue()).decode()
		
		return {
			"qr_code_base64": qr_base64,
			"message": "QR code generated successfully. Scan with your authenticator app."
		}
	except Exception as e:
		print(f"QR generation error for {current_user}: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to generate QR code")

@router.get("/me")
def get_me(
	current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
	user = db.query(User).filter_by(email=current_user).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return {"email": user.email}
