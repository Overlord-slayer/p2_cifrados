import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Header
from sqlalchemy.orm import Session
from app.schemas.schemas import UserCreate, UserOut, Token, UserLogin, SignupResponse, TOTPSetupResponse
from app.model.models import User
from app.db.db import get_db
from app.auth.utils import verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.totp import verify_totp_token
from app.auth.dependencies import get_current_user
import pyotp
import qrcode
import io
import base64
import logging
import time
from typing import Dict
from datetime import datetime, timedelta

from app.crypto.crypto import *

# Configure security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Rate limiting storage (in production, use Redis or similar)
login_attempts: Dict[str, list] = {}
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes

router = APIRouter(prefix="/auth", tags=["auth"])

def is_rate_limited(email: str) -> bool:
    """Check if email is rate limited due to failed login attempts"""
    if email not in login_attempts:
        return False
    
    current_time = datetime.now()
    # Remove old attempts (older than lockout duration)
    login_attempts[email] = [
        attempt_time for attempt_time in login_attempts[email]
        if current_time - attempt_time < timedelta(seconds=LOCKOUT_DURATION)
    ]
    
    return len(login_attempts[email]) >= MAX_ATTEMPTS

def record_failed_attempt(email: str):
    """Record a failed login attempt"""
    if email not in login_attempts:
        login_attempts[email] = []
    login_attempts[email].append(datetime.now())

def clear_failed_attempts(email: str):
    """Clear failed attempts for successful login"""
    if email in login_attempts:
        del login_attempts[email]

@router.post("/signup", response_model=SignupResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
	# Input validation
	if not user.email or not user.password:
		raise HTTPException(status_code=400, detail="Invalid request data")
	
	# Password strength validation
	if len(user.password) < 8:
		raise HTTPException(status_code=400, detail="Invalid request data")

	try:
		# Always perform the same operations to prevent timing attacks
		# This prevents user enumeration by ensuring consistent response time
		
		# Check if user exists
		db_user = db.query(User).filter(User.email == user.email).first()
		
		# Generate data regardless of whether user exists
		hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
		totp_secret = pyotp.random_base32()
		
		private_key, public_key = generate_rsa_keys()
		private_key_encrypted = encrypt_bytes(private_key)

		private_ecc_key, public_ecc_key = generate_ecc_keys()
		private_ecc_key_encrypted = encrypt_bytes(private_ecc_key)

		if db_user:
			# User exists - log security event but don't reveal this to client
			security_logger.warning(f"Signup attempt for existing email: {user.email}")
			raise HTTPException(status_code=400, detail="Invalid request data")

		# Create new user
		new_user = User(
			email=user.email,
			hashed_password=hashed_pw,
			totp_secret=totp_secret,
			public_key=bytes_to_str(public_key),
			private_key=bytes_to_str(private_key_encrypted),
			public_ecc_key=bytes_to_str(public_ecc_key),
			private_ecc_key=bytes_to_str(private_ecc_key_encrypted)
		)
		
		db.add(new_user)
		db.commit()
		db.refresh(new_user)

		# Log successful signup
		security_logger.info(f"Successful user signup: {user.email}")

		return {
			"email": new_user.email,
			"message": "Account created successfully. Please complete 2FA setup.",
			"setup_required": True
		}
		
	except HTTPException:
		raise
	except Exception as e:
		# Log detailed error internally but return generic message
		security_logger.error(f"Signup error for {user.email}: {str(e)}")
		raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Token)
def signin(login_data: UserLogin, db: Session = Depends(get_db)):
	# Input validation
	if not login_data.email or not login_data.password or not login_data.totp_code:
		raise HTTPException(status_code=400, detail="Invalid request data")
	
	# Check rate limiting
	if is_rate_limited(login_data.email):
		security_logger.warning(f"Rate limited login attempt for: {login_data.email}")
		raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
	
	try:
		# Always perform password hashing to prevent timing attacks
		# This ensures consistent response time regardless of user existence
		dummy_hash = bcrypt.hashpw("dummy".encode(), bcrypt.gensalt()).decode()
		
		user = db.query(User).filter_by(email=login_data.email).first()
		
		# Perform verification operations regardless of user existence
		if user:
			password_valid = verify_password(login_data.password, user.hashed_password)
			totp_valid = verify_totp_token(user.totp_secret, login_data.totp_code) if password_valid else False
		else:
			# Perform dummy operations to maintain consistent timing
			verify_password(login_data.password, dummy_hash)
			password_valid = False
			totp_valid = False

		if not user or not password_valid or not totp_valid:
			# Record failed attempt for rate limiting
			record_failed_attempt(login_data.email)
			
			# Log security event with details for monitoring
			security_logger.warning(f"Failed login attempt for: {login_data.email}")
			
			# Always return the same error to prevent user enumeration
			raise HTTPException(status_code=401, detail="Authentication failed")

		# Clear any previous failed attempts on successful login
		clear_failed_attempts(login_data.email)
		
		# Generate tokens
		access_token = create_access_token({"sub": user.email}, scope="user")
		refresh_token = create_refresh_token({"sub": user.email})

		# Log successful login
		security_logger.info(f"Successful login for: {user.email}")

		return {
			"access_token": access_token,
			"refresh_token": refresh_token,
			"token_type": "bearer",
		}
		
	except HTTPException:
		raise
	except Exception as e:
		# Log detailed error internally but return generic message
		security_logger.error(f"Login error for {login_data.email}: {str(e)}")
		raise HTTPException(status_code=500, detail="Authentication failed")

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
	payload = decode_token(refresh_token, expected_type="refresh")
	if not payload:
		raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

	email = payload.get("sub")
	user = db.query(User).filter_by(email=email).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")

	new_access_token = create_access_token({"sub": email}, scope="user")
	new_refresh_token = create_refresh_token({"sub": email})

	return {
		"access_token": new_access_token,
		"refresh_token": new_refresh_token,
		"token_type": "bearer",
	}

@router.get("/totp-setup", response_model=TOTPSetupResponse)
def get_totp_setup(
	current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
	"""
	Secure endpoint to get TOTP setup information.
	Only accessible to authenticated users.
	"""
	user = db.query(User).filter_by(email=current_user).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	
	try:
		# Generate QR code for TOTP setup
		uri = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(
			name=user.email, issuer_name="ChatSecureApp"
		)
		qr_img = qrcode.make(uri)
		buf = io.BytesIO()
		qr_img.save(buf, format="PNG")
		qr_base64 = base64.b64encode(buf.getvalue()).decode()

		# Log TOTP setup access
		security_logger.info(f"TOTP setup accessed by: {user.email}")

		return {
			"totp_secret": user.totp_secret,
			"qr_code_base64": qr_base64,
		}
		
	except Exception as e:
		security_logger.error(f"TOTP setup error for {user.email}: {str(e)}")
		raise HTTPException(status_code=500, detail="Setup failed")

@router.get("/me")
def get_me(
	current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
	user = db.query(User).filter_by(email=current_user).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return {"email": user.email}
