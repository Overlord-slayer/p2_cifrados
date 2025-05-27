from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
import json
import os

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

APP_SECRET = b"your-very-secure-app-secret"

def derive_key(secret: bytes, salt: bytes, length: int = 32) -> bytes:
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=length,
		salt=salt,
		iterations=100_000,
		backend=default_backend()
	)
	return kdf.derive(secret)

def encrypt_data(data: bytes, secret: bytes) -> bytes:
	salt = os.urandom(16)
	key = derive_key(secret, salt)
	iv = os.urandom(16)
	cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
	encryptor = cipher.encryptor()
	ciphertext = encryptor.update(data) + encryptor.finalize()
	return salt + iv + ciphertext  # Pack salt+iv+ciphertext

def decrypt_data(encrypted: bytes, secret: bytes) -> bytes:
	salt = encrypted[:16]
	iv = encrypted[16:32]
	ciphertext = encrypted[32:]
	key = derive_key(secret, salt)
	cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
	decryptor = cipher.decryptor()
	return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt_private_key(private_key, app_secret: bytes):
	pem = private_key.private_bytes(
		encoding=serialization.Encoding.PEM,
		format=serialization.PrivateFormat.PKCS8,
		encryption_algorithm=serialization.NoEncryption()
	)
	return encrypt_data(pem, app_secret)

def decrypt_private_key(encrypted_data: bytes, app_secret: bytes):
	decrypted_pem = decrypt_data(encrypted_data, app_secret)
	return serialization.load_pem_private_key(decrypted_pem, password=None, backend=default_backend())

def generate_rsa_keys():
	private_key = rsa.generate_private_key(
		public_exponent=65537, key_size=2048, backend=default_backend()
	)
	public_key = private_key.public_key()
	return private_key, public_key

def cifrar_mensaje_individual(mensaje: str, clave_publica_rsa_pem: str) -> str:
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

	data = {
		'mensaje': base64.b64encode(mensaje_cifrado).decode(),
		'clave_aes': base64.b64encode(clave_aes_cifrada).decode(),
		'iv': base64.b64encode(iv).decode()
	}
	return json.dumps(data)

def descifrar_mensaje_individual(data_str: str, clave_privada_rsa_pem: str) -> str:
	data = json.loads(data_str)
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

def cifrar_mensaje_grupal(mensaje: str, clave_simetrica: bytes) -> str:
	aesgcm = AESGCM(clave_simetrica)
	nonce = get_random_bytes(12)
	mensaje_cifrado = aesgcm.encrypt(nonce, mensaje.encode(), None)
	data = {
		'mensaje': base64.b64encode(mensaje_cifrado).decode(),
		'nonce': base64.b64encode(nonce).decode()
	}
	return json.dumps(data)

def descifrar_mensaje_grupal(data_str: str, clave_simetrica: bytes) -> str:
	try:
		data = json.loads(data_str)
		aesgcm = AESGCM(clave_simetrica)
		nonce = base64.b64decode(data['nonce'])
		mensaje_cifrado = base64.b64decode(data['mensaje'])
		return aesgcm.decrypt(nonce, mensaje_cifrado, None).decode()
	except:
		return data_str

def bytes_to_str(data: bytes) -> str:
	return base64.b64encode(data).decode('utf-8')

def str_to_bytes(data_str: str) -> bytes:
	return base64.b64decode(data_str)