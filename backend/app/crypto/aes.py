from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# --- AES Generate 256 bit Key ---
def aes_key():
	return os.urandom(32)

# --- AES Encryption Function (AES-GCM) ---
def aes_encrypt(message: bytes, key: bytes):
	iv = os.urandom(12)  # Generate a random 12-byte IV
	encryptor = Cipher(
		algorithms.AES(key),
		modes.GCM(iv),
		backend=default_backend()
	).encryptor()
	
	ciphertext = encryptor.update(message) + encryptor.finalize()
	return {
		'ciphertext': ciphertext,
		'iv': iv,
		'tag': encryptor.tag
	}

# --- AES Decryption Function (AES-GCM) ---
def aes_decrypt(encrypted_data: dict, key: bytes):
	decryptor = Cipher(
		algorithms.AES(key),
		modes.GCM(encrypted_data['iv'], encrypted_data['tag']),
		backend=default_backend()
	).decryptor()
	
	plaintext = decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()
	return plaintext