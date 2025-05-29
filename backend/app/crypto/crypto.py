from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from dotenv import load_dotenv
import hashlib
import base64
import json
import os

from cryptography.hazmat.backends import default_backend

load_dotenv()
APP_SECRET = os.getenv("APP_SECRET")

def generate_key() -> bytes:
	hash_digest = hashlib.sha256(APP_SECRET.encode()).digest()
	return base64.urlsafe_b64encode(hash_digest)

def encrypt_bytes(data: bytes) -> bytes:
	key = generate_key()
	fernet = Fernet(key)
	encrypted = fernet.encrypt(data)
	return encrypted

def decrypt_bytes(data: bytes) -> bytes:
	key = generate_key()
	fernet = Fernet(key)
	decrypted = fernet.decrypt(data)
	return decrypted

def generate_rsa_keys():
	key = RSA.generate(2048)
	private_pem = key.export_key()
	public_pem = key.publickey().export_key()
	return private_pem, public_pem

def cifrar_mensaje_individual(mensaje: str, clave_publica_rsa_pem: bytes) -> str:
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

def descifrar_mensaje_individual(data_str: str, clave_privada_rsa_pem: bytes) -> str:
	try:
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
	except Exception as e:
		print("\n"+"-"*50+"\n"+str(e)+"\n"+"-"*50)
		return data_str

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
	except Exception as e:
		print("\n"+"-"*50+"\n"+str(e)+"\n"+"-"*50)
		return data_str

def bytes_to_str(data: bytes) -> str:
	return base64.urlsafe_b64encode(data).decode()

def str_to_bytes(data_str: str) -> bytes:
	return base64.urlsafe_b64decode(data_str)