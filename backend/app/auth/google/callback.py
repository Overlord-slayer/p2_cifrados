from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.model.models import User
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.google.oauth2 import oauth
from fastapi.responses import RedirectResponse
import logging

import pyotp

from app.crypto.crypto import *

router = APIRouter(prefix="/auth", tags=["google"])
logger = logging.getLogger(__name__)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
	"""
	OAuth callback con manejo de errores genérico.
	Errores detallados solo en logs del servidor.
	"""
	try:
		token = await oauth.google.authorize_access_token(request)

		# Obtener la información del usuario desde Google
		user_info = await oauth.google.userinfo(token=token)

		if not user_info:
			logger.error("Google userinfo returned None")
			raise HTTPException(status_code=400, detail="Authentication failed")

		email = user_info.get("email")
		if not email:
			logger.error(f"Email not found in Google response: {user_info}")
			raise HTTPException(status_code=400, detail="Authentication failed")

		# Buscar si el usuario ya existe en la base de datos
		user = db.query(User).filter_by(email=email).first()

		if user:
			# Si el usuario ya existe y es una cuenta de Google, solo autenticamos
			if user.is_google_account:
				logger.info(f"OAuth login: existing Google user {email}")
				access_token = create_access_token({"sub": email})
				refresh_token = create_refresh_token({"sub": email})

				return RedirectResponse(
					url=f"http://localhost:3000/oauth-callback?access_token={access_token}&refresh_token={refresh_token}&totp_enabled={bool(user.totp_secret)}"
				)
			else:
				# Si el usuario ya existe y no es una cuenta de Google, asociamos la cuenta a Google
				logger.info(f"Linking existing account to Google: {email}")
				user.is_google_account = True
				db.commit()
				db.refresh(user)
		else:
			# Si no existe, crear una nueva cuenta de usuario con is_google_account como True
			logger.info(f"Creating new Google user: {email}")
			totp_secret = pyotp.random_base32()

			private_key, public_key = generate_rsa_keys()
			private_key_encrypted = encrypt_bytes(private_key)

			private_ecc_key, public_ecc_key = generate_ecc_keys()
			private_ecc_key_encrypted = encrypt_bytes(private_ecc_key)

			user = User(
				email=email,
				hashed_password="",
				totp_secret=totp_secret,
				is_google_account=True,
				public_key=bytes_to_str(public_key),
				private_key=bytes_to_str(private_key_encrypted),
				public_ecc_key=bytes_to_str(public_ecc_key),
				private_ecc_key=bytes_to_str(private_ecc_key_encrypted)
			)
			db.add(user)
			db.commit()
			db.refresh(user)

		# Crear tokens JWT
		access_token = create_access_token({"sub": email})
		refresh_token = create_refresh_token({"sub": email})

		# Redirigir al frontend con los tokens
		return RedirectResponse(
			url=f"http://localhost:3000/oauth-callback?access_token={access_token}&refresh_token={refresh_token}&totp_enabled={bool(user.totp_secret)}"
		)
	
	except HTTPException:
		# Re-raise HTTPExceptions ya manejadas
		raise
	except Exception as e:
		# Log detallado en servidor, mensaje genérico al cliente
		logger.exception(f"OAuth callback error: {e}")
		raise HTTPException(status_code=400, detail="Authentication failed")
