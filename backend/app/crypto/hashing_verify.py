from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.backends import default_backend

# --- Hashing Function (SHA-256) ---
def generate_hash(data: bytes):
	digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
	digest.update(data)
	return digest.finalize()

# --- Hash Verification Function ---
def verify_hash(data: bytes, expected_hash: bytes):
	calculated_hash = generate_hash(data)
	return calculated_hash == expected_hash

# --- HMAC Hashing Function (SHA-256) ---
def generate_hmac(key: bytes, data: bytes):
	h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
	h.update(data)
	return h.finalize()

# --- HMAC Hash Verification Function ---
def verify_hmac(key: bytes, data: bytes, expected_hmac: bytes):
	calculated_hmac = generate_hmac(key, data)
	return calculated_hmac == expected_hmac