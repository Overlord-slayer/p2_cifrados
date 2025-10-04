import bcrypt
from fastapi import APIRouter, Request, Depends, HTTPException
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
from app.utils.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=SignupResponse)
@limiter.limit("1/30seconds")
def signup(request: Request, user: UserCreate, db: Session = Depends(get_db)):
	"""
	Antienumeración: Siempre devuelve 200 con formato uniforme.
	No revela si el email ya existe o no.
	"""
	if not user.email or not user.password:
		raise HTTPException(status_code=400, detail="Email and password are required")

	# Verifica si el correo ya está registrado
	db_user = db.query(User).filter(User.email == user.email).first()
	if db_user:
		# Usuario ya existe - log en servidor, respuesta genérica al cliente
		logger.info(f"Signup attempt for existing email: {user.email}")
		return {
			"detail": "Solicitud recibida",
			"created": False
		}

	try:
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

		# Crear URI y QR base64
		uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
			name=user.email, issuer_name="ChatSecureApp"
		)
		qr_img = qrcode.make(uri)
		buf = io.BytesIO()
		qr_img.save(buf, format="PNG")
		qr_base64 = base64.b64encode(buf.getvalue()).decode()

		logger.info(f"New user created: {new_user.email}")
		return {
			"detail": "Solicitud recibida",
			"created": True,
			"email": new_user.email,
			"totp_secret": totp_secret,
			"qr_code_base64": qr_base64,
		}
	except Exception as e:
		# Log detallado en servidor, respuesta genérica al cliente
		logger.exception(f"Signup error for {user.email}: {e}")
		raise HTTPException(status_code=500, detail="Error procesando solicitud")

@router.post("/login", response_model=Token)
@limiter.limit("1/5seconds")
def signin(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
	"""
	Antienumeración: Todos los fallos (email inexistente, password incorrecta, TOTP incorrecto)
	devuelven el mismo mensaje genérico. Log detallado solo en servidor.
	"""
	user = db.query(User).filter_by(email=login_data.email).first()
	
	# Email no existe
	if not user:
		logger.warning(f"Login attempt for non-existent user: {login_data.email}")
		raise HTTPException(status_code=401, detail="Credenciales no válidas")
	
	# Password incorrecta
	if not verify_password(login_data.password, user.hashed_password):
		logger.warning(f"Invalid password for user: {login_data.email}")
		raise HTTPException(status_code=401, detail="Credenciales no válidas")

	# TOTP incorrecto
	if not verify_totp_token(user.totp_secret, login_data.totp_code):
		logger.warning(f"Invalid TOTP for user: {login_data.email}")
		raise HTTPException(status_code=401, detail="Credenciales no válidas")

	# Login exitoso
	logger.info(f"Successful login: {user.email}")
	access_token = create_access_token({"sub": user.email}, scope="user")
	refresh_token = create_refresh_token({"sub": user.email})

	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"token_type": "bearer",
	}

@router.post("/refresh", response_model=Token)
@limiter.limit("1/second")
def refresh_token_endpoint(
	request: Request, refresh_token: str = Header(...), db: Session = Depends(get_db)
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
@limiter.limit("1/second")
def get_me(
	request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
	user = db.query(User).filter_by(email=current_user).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return {"email": user.email}
