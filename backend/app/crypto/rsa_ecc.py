from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# --- RSA Key Generation ---
def generate_rsa_keys():
	private_key = rsa.generate_private_key(
		public_exponent=65537,
		key_size=2048,
		backend=default_backend()
	)
	public_key = private_key.public_key()
	return private_key, public_key

# --- ECC Key Generation ---
def generate_ecc_keys():
	private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
	public_key = private_key.public_key()
	return private_key, public_key

# --- Hybrid Encrypt Function ---
def hybrid_encrypt(message: bytes, rsa_pub_key, ecc_receiver_pub_key):
	# Ephemeral ECC key pair
	eph_priv_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
	shared_key = eph_priv_key.exchange(ec.ECDH(), ecc_receiver_pub_key)

	# Derive AES key
	aes_key = HKDF(
		algorithm=hashes.SHA256(),
		length=32,
		salt=None,
		info=b"hybrid-enc",
		backend=default_backend()
	).derive(shared_key)

	# Encrypt message with AES-GCM
	iv = os.urandom(12)
	encryptor = Cipher(
		algorithms.AES(aes_key), 
		modes.GCM(iv), 
		backend=default_backend()
	).encryptor()
	ciphertext = encryptor.update(message) + encryptor.finalize()

	# Serialize ephemeral ECC public key
	eph_pub_bytes = eph_priv_key.public_key().public_bytes(
		serialization.Encoding.PEM,
		serialization.PublicFormat.SubjectPublicKeyInfo
	)

	# Encrypt ephemeral ECC public key using RSA
	encrypted_ecc_key = rsa_pub_key.encrypt(
		eph_pub_bytes,
		padding.OAEP(
			mgf=padding.MGF1(algorithm=hashes.SHA256()),
			algorithm=hashes.SHA256(),
			label=None
		)
	)

	return {
		'ciphertext': ciphertext,
		'iv': iv,
		'tag': encryptor.tag,
		'encrypted_ecc_key': encrypted_ecc_key
	}

# --- Hybrid Decrypt Function ---
def hybrid_decrypt(encrypted_data: dict, rsa_priv_key, ecc_receiver_priv_key):
	# Decrypt ephemeral ECC public key with RSA
	eph_pub_bytes = rsa_priv_key.decrypt(
		encrypted_data['encrypted_ecc_key'],
		padding.OAEP(
			mgf=padding.MGF1(algorithm=hashes.SHA256()),
			algorithm=hashes.SHA256(),
			label=None
		)
	)

	eph_pub_key = serialization.load_pem_public_key(eph_pub_bytes, backend=default_backend())

	# Derive shared key using ECDH
	shared_key = ecc_receiver_priv_key.exchange(ec.ECDH(), eph_pub_key)

	aes_key = HKDF(
		algorithm=hashes.SHA256(),
		length=32,
		salt=None,
		info=b"hybrid-enc",
		backend=default_backend()
	).derive(shared_key)

	# Decrypt AES-GCM message
	decryptor = Cipher(
		algorithms.AES(aes_key),
		modes.GCM(encrypted_data['iv'], encrypted_data['tag']),
		backend=default_backend()
	).decryptor()

	plaintext = decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()
	return plaintext