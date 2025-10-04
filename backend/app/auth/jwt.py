"""
jwt_utils.py

Módulo para la creación y validación de access tokens y refresh tokens usando JSON Web Tokens (JWT),
utilizando la biblioteca `python-jose`.

Soporta:
- Expiración automática
- Campo `scope` para roles/permisos
- Campo `aud` para audiencia esperada
- Tokens de acceso y refresh diferenciados
- Claims robustos: exp, iat, nbf, jti, iss, aud, type
- Revocación de tokens (Redis o memoria)

Requiere las siguientes variables de entorno definidas en `.env`:
- SECRET_KEY: Clave secreta usada para firmar los tokens JWT.
- JWT_ISSUER: Emisor del token (opcional, default: "chatapp-backend")
- JWT_AUDIENCE: Audiencia del token (opcional, default: "chatapp-client")
- REDIS_URL: URL de Redis para revocación (opcional)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Literal, Set
from jose import JWTError, jwt
import os
import uuid
import logging
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
DEFAULT_AUDIENCE = os.getenv("JWT_AUDIENCE", "chatapp-client")
DEFAULT_ISSUER = os.getenv("JWT_ISSUER", "chatapp-backend")
REDIS_URL = os.getenv("REDIS_URL")

# Sistema de revocación en memoria (fallback si no hay Redis)
_blacklist: Set[str] = set()
_MAX_BLACKLIST_SIZE = 10000

# Intentar conexión a Redis si está configurado
_redis_client = None
if REDIS_URL:
    try:
        import redis
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        _redis_client.ping()
        logger.info("Redis connected for JWT revocation")
    except Exception as e:
        logger.warning(f"Redis connection failed, using in-memory blacklist: {e}")
        _redis_client = None

# Hooks que debes implementar con tu storage (ej. Redis/DB)
# signature: (jti: str) -> None
def register_jti_in_store(jti: str, expires_at: datetime, token_type: str):
	"""
	Crea un token JWT con claims robustos y expiración configurada.
	Incluye: exp, iat, nbf, jti, iss, aud, type

	Args:
		data (dict): Diccionario con los datos del payload. Debe incluir al menos `sub`.
		expires_delta (timedelta): Tiempo hasta la expiración del token.
		token_type (Literal["access", "refresh"]): Tipo de token, útil para validación y logs.
		audience (Optional[str]): Valor del campo `aud` (audiencia) del token.

	Returns:
		str: Token JWT firmado.
	"""
	to_encode = data.copy()
	now = datetime.now(timezone.utc)
	expire = now + expires_delta
	
	# Claims robustos según estándares JWT
	to_encode.update({
		"exp": expire,           # Expiration time
		"iat": now,              # Issued at
		"nbf": now,              # Not before
		"jti": str(uuid.uuid4()), # JWT ID único
		"iss": DEFAULT_ISSUER,   # Issuer
		"aud": audience,         # Audience
		"type": token_type       # Token type
	})
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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
) -> Optional[dict]:
	"""
	Valida y decodifica un JWT. Verifica todos los claims robustos:
	- Firma, expiración (exp), emisión (iat), no-antes (nbf)
	- Issuer (iss), Audience (aud), Type (type)
	- Revocación (jti no está en blacklist)

	Args:
		token (str): Token JWT a decodificar.
		expected_type (str): Tipo esperado ("access" o "refresh").
		audience (Optional[str]): Audiencia esperada (`aud`).

	Returns:
		dict | None: Payload del token si es válido; `None` si es inválido.
	"""
	try:
		# Validar firma, exp, nbf, aud automáticamente
		payload = jwt.decode(
			token, 
			SECRET_KEY, 
			algorithms=[ALGORITHM], 
			audience=audience,
			issuer=DEFAULT_ISSUER,
			options={
				"verify_signature": True,
				"verify_exp": True,
				"verify_nbf": True,
				"verify_iat": True,
				"verify_aud": True,
				"verify_iss": True
			}
		)
		
		# Validar tipo de token
		if payload.get("type") != expected_type:
			logger.warning(f"Token type mismatch: expected {expected_type}, got {payload.get('type')}")
			return None
		
		# Validar que el token no está revocado
		jti = payload.get("jti")
		if jti and is_token_revoked(jti):
			logger.warning(f"Token revoked: jti={jti}")
			return None
			
		return payload
	except JWTError as e:
		logger.debug(f"JWT validation failed: {e}")
		return None

def get_subject_from_token(token: str) -> Optional[str]:
	payload = decode_token(token)
	if payload:
		return payload.get("sub")
	return None


def revoke_token(jti: str, exp: datetime) -> None:
	"""
	Revoca un token añadiéndolo a la blacklist.
	
	Si Redis está disponible, usa Redis con TTL hasta exp.
	Si no, usa set en memoria con limpieza básica.
	
	Args:
		jti (str): JWT ID único del token
		exp (datetime): Fecha de expiración del token
	"""
	global _blacklist
	
	if _redis_client:
		try:
			# Calcular TTL hasta expiración
			ttl_seconds = int((exp - datetime.now(timezone.utc)).total_seconds())
			if ttl_seconds > 0:
				_redis_client.setex(f"jwt:blacklist:{jti}", ttl_seconds, "1")
				logger.info(f"Token revoked in Redis: jti={jti}")
			return
		except Exception as e:
			logger.error(f"Redis revocation failed, using memory: {e}")
	
	# Fallback: memoria
	_blacklist.add(jti)
	
	# Limpieza simple si crece mucho
	if len(_blacklist) > _MAX_BLACKLIST_SIZE:
		# Eliminar primeros 1000 elementos (FIFO aproximado)
		_blacklist.difference_update(list(_blacklist)[:1000])
		logger.warning(f"Blacklist memory cleaned, size: {len(_blacklist)}")


def is_token_revoked(jti: str) -> bool:
	"""
	Verifica si un token está revocado.
	
	Args:
		jti (str): JWT ID único del token
		
	Returns:
		bool: True si está revocado, False si no
	"""
	if _redis_client:
		try:
			return _redis_client.exists(f"jwt:blacklist:{jti}") > 0
		except Exception as e:
			logger.error(f"Redis check failed, checking memory: {e}")
	
	return jti in _blacklist
