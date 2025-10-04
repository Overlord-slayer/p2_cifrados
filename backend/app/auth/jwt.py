# jwt_utils_improved.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal, Callable, Dict, Any
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
import uuid
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Config
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
	raise RuntimeError("SECRET_KEY no definido. Configure una clave segura en el entorno (ej. desde Vault).")

# Recomendación: preferir RS256 y cargar claves desde archivos/secret manager
# ALGORITHM = "RS256"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
DEFAULT_AUDIENCE = "yourapp-client"
ISSUER = "yourapp.example.com"  # fija el issuer de forma explícita

# Hooks que debes implementar con tu storage (ej. Redis/DB)
# signature: (jti: str) -> None
def register_jti_in_store(jti: str, expires_at: datetime, token_type: str):
	"""
	Guarda jti con expiración; implementación depende de tu storage.
	Ejemplo: Redis SET jti -> token metadata EX seconds
	"""
	raise NotImplementedError

# signature: (jti: str) -> bool
def is_jti_revoked(jti: str) -> bool:
	"""
	Comprueba si el jti ha sido revocado (devuelve True si revocado).
	"""
	raise NotImplementedError

def _now_utc() -> datetime:
	return datetime.now(timezone.utc)

def _new_jti() -> str:
	return str(uuid.uuid4())

def create_token(
	data: Dict[str, Any],
	expires_delta: timedelta,
	token_type: Literal["access", "refresh"] = "access",
	audience: Optional[str] = DEFAULT_AUDIENCE,
) -> str:
	payload = data.copy()  # no mutamos el input
	now = _now_utc()
	expire = now + expires_delta
	jti = _new_jti()
	# solo permitir claims concretos o usar prefijo para custom claims
	# añadir claims estándares
	payload.update({
		"exp": expire,
		"iat": now,
		"nbf": now,
		"jti": jti,
		"type": token_type,
		"aud": audience,
		"iss": ISSUER,
	})
	token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
	# registrar jti (para revocación/rotación)
	try:
		register_jti_in_store(jti, expire, token_type)
	except Exception as e:
		# si falla el registro, loggear y decidir si permitir emisión (aquí lo permitimos pero registralo en monitor)
		logger.exception("No se pudo registrar jti en store: %s", e)
	return token

def create_access_token(data: Dict[str, Any], scope: str = "user", audience: Optional[str] = DEFAULT_AUDIENCE) -> str:
	payload = data.copy()
	payload["scope"] = scope
	return create_token(payload, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access", audience)

def create_refresh_token(data: Dict[str, Any], audience: Optional[str] = DEFAULT_AUDIENCE) -> str:
	payload = data.copy()
	return create_token(payload, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh", audience)

def decode_token(
	token: str,
	expected_type: str = "access",
	audience: Optional[str] = DEFAULT_AUDIENCE,
	require_issuer: Optional[str] = ISSUER,
	revoked_check: bool = True,
) -> Optional[Dict[str, Any]]:
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=audience)
		# validamos issuer si es requerido
		if require_issuer and payload.get("iss") != require_issuer:
			logger.warning("Token con issuer inesperado: %s", payload.get("iss"))
			return None
		if payload.get("type") != expected_type:
			logger.warning("Token con tipo inesperado: %s", payload.get("type"))
			return None
		jti = payload.get("jti")
		if revoked_check and jti:
			try:
				if is_jti_revoked(jti):
					logger.info("Token revocado (jti=%s)", jti)
					return None
			except Exception:
				logger.exception("Error comprobando revocación jti")
				# por seguridad, negar si no podemos comprobar la revocación
				return None
		return payload
	except JWTError as e:
		logger.info("JWTError al decodificar token: %s", e)
		return None

def get_subject_from_token(token: str) -> Optional[str]:
	payload = decode_token(token)
	if payload:
		return payload.get("sub")
	return None