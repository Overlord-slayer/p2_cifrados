from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_rsa_keys():
	private_key = rsa.generate_private_key(
		public_exponent=65537, key_size=2048, backend=default_backend()
	)
	public_key = private_key.public_key()
	return private_key, public_key

def cifrar_mensaje_individual(mensaje: str, clave_publica_rsa_pem: str) -> dict:
	# Genera clave AES-256 aleatoria
	clave_aes = get_random_bytes(32)
	iv = get_random_bytes(16)

	# Cifra mensaje con AES-256-CBC
	cipher_aes = AES.new(clave_aes, AES.MODE_CBC, iv)
	padding_len = 16 - len(mensaje.encode()) % 16
	mensaje_padded = mensaje + chr(padding_len) * padding_len
	mensaje_cifrado = cipher_aes.encrypt(mensaje_padded.encode())

	# Cifra clave AES con clave pública RSA
	rsa_key = RSA.import_key(clave_publica_rsa_pem)
	cipher_rsa = PKCS1_OAEP.new(rsa_key)
	clave_aes_cifrada = cipher_rsa.encrypt(clave_aes)

	return {
		'mensaje': base64.b64encode(mensaje_cifrado).decode(),
		'clave_aes': base64.b64encode(clave_aes_cifrada).decode(),
		'iv': base64.b64encode(iv).decode()
	}

def descifrar_mensaje_individual(data: dict, clave_privada_rsa_pem: str) -> str:
	clave_aes_cifrada = base64.b64decode(data['clave_aes'])
	mensaje_cifrado = base64.b64decode(data['mensaje'])
	iv = base64.b64decode(data['iv'])

	# Descifra clave AES
	rsa_key = RSA.import_key(clave_privada_rsa_pem)
	cipher_rsa = PKCS1_OAEP.new(rsa_key)
	clave_aes = cipher_rsa.decrypt(clave_aes_cifrada)

	# Descifra mensaje
	cipher_aes = AES.new(clave_aes, AES.MODE_CBC, iv)
	mensaje_padded = cipher_aes.decrypt(mensaje_cifrado)
	padding_len = mensaje_padded[-1]
	return mensaje_padded[:-padding_len].decode()


def cifrar_mensaje_grupal(mensaje: str, clave_simetrica: bytes) -> dict:
	aesgcm = AESGCM(clave_simetrica)
	nonce = get_random_bytes(12)
	mensaje_cifrado = aesgcm.encrypt(nonce, mensaje.encode(), None)
	return {
		'mensaje': base64.b64encode(mensaje_cifrado).decode(),
		'nonce': base64.b64encode(nonce).decode()
	}

def descifrar_mensaje_grupal(data: dict, clave_simetrica: bytes) -> str:
	aesgcm = AESGCM(clave_simetrica)
	nonce = base64.b64decode(data['nonce'])
	mensaje_cifrado = base64.b64decode(data['mensaje'])
	return aesgcm.decrypt(nonce, mensaje_cifrado, None).decode()

def string_to_base64_bytes(texto: str) -> bytes:
	return base64.b64encode(texto.encode('utf-8'))

def base64_bytes_to_string(b64_bytes: bytes) -> str:
	return base64.b64decode(b64_bytes).decode('utf-8')