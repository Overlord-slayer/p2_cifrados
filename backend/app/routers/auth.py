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

from app.crypto.crypto import *

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=SignupResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
	if not user.email or not user.password:
		raise HTTPException(status_code=400, detail="Email and password are required")

	# Verifica si el correo ya está registrado
	db_user = db.query(User).filter(User.email == user.email).first()
	if db_user:
		raise HTTPException(status_code=400, detail="Email already registered")

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

		# Crear URI y QR base64
		uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
			name=user.email, issuer_name="ChatSecureApp"
		)
		qr_img = qrcode.make(uri)
		buf = io.BytesIO()
		qr_img.save(buf, format="PNG")
		qr_base64 = base64.b64encode(buf.getvalue()).decode()

		return {
			"email": new_user.email,
			"totp_secret": totp_secret,
			"qr_code_base64": qr_base64,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/login", response_model=Token)
def signin(login_data: UserLogin, db: Session = Depends(get_db)):
	user = db.query(User).filter_by(email=login_data.email).first()
	if not user or not verify_password(login_data.password, user.hashed_password):
		raise HTTPException(status_code=401, detail="Invalid credentials")

	if not verify_totp_token(user.totp_secret, login_data.totp_code):
		raise HTTPException(status_code=401, detail="Invalid 2FA code")

	# Crear tokens
	access_token = create_access_token({"sub": user.email}, scope="user")
	refresh_token = create_refresh_token({"sub": user.email})

	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"token_type": "bearer",
	}

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

@router.get("/me")
def get_me(
	current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
	user = db.query(User).filter_by(email=current_user).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return {"email": user.email}