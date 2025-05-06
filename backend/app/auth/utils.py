from passlib.context import CryptContext

# Configura el contexto de hash con el algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""
	Verifica que una contraseña en texto plano coincida con su hash almacenado.

	Args:
		plain_password (str): La contraseña proporcionada por el usuario (texto plano).
		hashed_password (str): El hash de la contraseña almacenado en la base de datos.

	Returns:
		bool: True si la contraseña coincide con el hash, False en caso contrario.

	Uso:
		>>> verify_password("secreta123", "$2b$12$e6vhqi...")

	Seguridad:
		Esta función utiliza el contexto de Passlib para manejar internamente
		sal y comparación segura evitando ataques de tiempo.
	"""
	return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
	"""
	Genera un hash seguro para una contraseña en texto plano utilizando bcrypt.

	Args:
		password (str): La contraseña del usuario en texto plano.

	Returns:
		str: El hash bcrypt generado que debe almacenarse en la base de datos.

	Uso:
		>>> get_password_hash("secreta123")
		'$2b$12$e6vhqi3...'

	Seguridad:
		Utiliza bcrypt con sal automática y múltiples rondas de hashing.
		Ideal para almacenamiento seguro de credenciales.
	"""
	return pwd_context.hash(password)