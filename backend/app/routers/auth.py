import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Header
from sqlalchemy.orm import Session
from app.schemas.schemas import UserCreate, UserOut, Token, UserLogin, SignupResponse
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

from app.crypto.crypto import *

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=SignupResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
	if not user.email or not user.password:
		raise HTTPException(status_code=400, detail="Invalid input")

	try:
		# Generate a non-sensitive identifier for response
		setup_id = base64.b64encode(f"setup_{user.email}".encode()).decode()[:16]
		
		# Verifica si el correo ya está registrado
		db_user = db.query(User).filter(User.email == user.email).first()
		if db_user:
			# Return same response for existing emails (but don't actually register)
			return {
				"email": user.email,
				"totp_secret": setup_id,
				"qr_code_base64": setup_id,
			}

		# Proceed with actual registration for new users
		hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
		totp_secret = pyotp.random_base32()

		private_key, public_key = generate_rsa_keys()
		private_key_encrypted = encrypt_bytes(private_key)

		private_ecc_key, public_ecc_key = generate_ecc_keys()
		private_ecc_key_encrypted = encrypt_bytes(private_ecc_key)

		# Create SQLAlchemy user object
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

		return {
			"email": new_user.email,
			"totp_secret": setup_id,  # Return only non-sensitive identifier
			"qr_code_base64": setup_id,  # Return only non-sensitive identifier
		}
	except HTTPException:
		# Re-raise HTTPExceptions as-is
		raise
	except Exception as e:
		logger.exception("Signup failure")
		# 500 sólo si realmente es un error interno
		raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", response_model=Token)
def signin(login_data: UserLogin, db: Session = Depends(get_db)):
	try:
		user = db.query(User).filter_by(email=login_data.email).first()
		if not user or not verify_password(login_data.password, user.hashed_password):
			raise HTTPException(status_code=401, detail="Credenciales no válidas")

		if not verify_totp_token(user.totp_secret, login_data.totp_code):
			raise HTTPException(status_code=401, detail="Credenciales no válidas")

		# Crear tokens
		access_token = create_access_token({"sub": user.email}, scope="user")
		refresh_token = create_refresh_token({"sub": user.email})

		return {
			"access_token": access_token,
			"refresh_token": refresh_token,
			"token_type": "bearer",
		}
	except HTTPException:
		# Re-raise HTTPExceptions as-is
		raise
	except Exception as e:
		logger.exception("Login failure")
		# 500 sólo si realmente es un error interno
		raise HTTPException(status_code=500, detail="Internal server error")

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
			raise HTTPException(status_code=401, detail="Credenciales no válidas")

		email = payload.get("sub")
		user = db.query(User).filter_by(email=email).first()
		if not user:
			raise HTTPException(status_code=401, detail="Credenciales no válidas")

		new_access_token = create_access_token({"sub": email}, scope="user")
		new_refresh_token = create_refresh_token({"sub": email})

		return {
			"access_token": new_access_token,
			"refresh_token": new_refresh_token,
			"token_type": "bearer",
		}
	except HTTPException:
		# Re-raise HTTPExceptions as-is
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me")
def get_me(
	current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
	try:
		user = db.query(User).filter_by(email=current_user).first()
		if not user:
			raise HTTPException(status_code=404, detail="Resource not found")
		return {"email": user.email}
	except HTTPException:
		# Re-raise HTTPExceptions as-is
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")
