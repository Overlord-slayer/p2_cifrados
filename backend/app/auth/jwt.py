"""
jwt_utils.py

Módulo para la creación y validación de access tokens y refresh tokens usando JSON Web Tokens (JWT),
utilizando la biblioteca `python-jose`.

Soporta:
- Expiración automática
- Campo `scope` para roles/permisos
- Campo `aud` para audiencia esperada
- Tokens de acceso y refresh diferenciados

Requiere las siguientes variables de entorno definidas en `.env`:
- SECRET_KEY: Clave secreta usada para firmar los tokens JWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Literal
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
DEFAULT_AUDIENCE = "yourapp-client"

def create_token(
	data: dict,
	expires_delta: timedelta,
	token_type: Literal["access", "refresh"] = "access",
	audience: Optional[str] = DEFAULT_AUDIENCE,
) -> str:
	"""
	Crea un token JWT con los campos estándar y expiración configurada.

	Args:
		data (dict): Diccionario con los datos del payload. Debe incluir al menos `sub`.
		expires_delta (timedelta): Tiempo hasta la expiración del token.
		token_type (Literal["access", "refresh"]): Tipo de token, útil para validación y logs.
		audience (Optional[str]): Valor del campo `aud` (audiencia) del token.

	Returns:
		str: Token JWT firmado.
	"""
	to_encode = data.copy()
	expire = datetime.now(timezone.utc) + expires_delta
	to_encode.update({"exp": expire, "type": token_type, "aud": audience})
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(
	data: dict, scope: str = "user", audience: Optional[str] = DEFAULT_AUDIENCE
) -> str:
	"""
	Crea un token de acceso con expiración corta.

	Args:
		data (dict): Debe incluir `"sub"` (por ejemplo, ID de usuario).
		scope (str): Rol o permisos asociados al token (ej. "admin", "user").
		audience (Optional[str]): Audiencia para la que es válido el token.

	Returns:
		str: JWT de acceso.
	"""
	data["scope"] = scope
	return create_token(
		data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access", audience
	)

def create_refresh_token(data: dict, audience: Optional[str] = DEFAULT_AUDIENCE) -> str:
	"""
	Crea un refresh token con expiración prolongada.

	Args:
		data (dict): Debe incluir `"sub"`.
		audience (Optional[str]): Audiencia esperada.

	Returns:
		str: JWT de refresh.
	"""
	return create_token(
		data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh", audience
	)

def decode_token(
	token: str,
	expected_type: str = "access",
	audience: Optional[str] = DEFAULT_AUDIENCE,
) -> Optional[dict]:
	"""
	Valida y decodifica un JWT. Verifica la firma, expiración, tipo de token y audiencia.

	Args:
		token (str): Token JWT a decodificar.
		expected_type (str): Tipo esperado ("access" o "refresh").
		audience (Optional[str]): Audiencia esperada (`aud`).

	Returns:
		dict | None: Payload del token si es válido; `None` si es inválido.
	"""
	try:
		payload = jwt.decode(
			token, SECRET_KEY, algorithms=[ALGORITHM], audience=audience
		)
		if payload.get("type") != expected_type:
			return None
		return payload
	except JWTError:
		return None

def get_subject_from_token(token: str) -> Optional[str]:
	"""
	Extrae el valor del campo `sub` desde un JWT válido.

	Args:
		token (str): JWT codificado.

	Returns:
		str | None: ID del sujeto (`sub`) o `None` si no es válido.
	"""
	payload = decode_token(token)
	if payload:
		return payload.get("sub")
	return None