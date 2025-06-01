from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend

def generate_hash(data: bytes):
	digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
	digest.update(data)
	return digest.finalize()

def verify_hash(data: bytes, expected_hash: bytes):
	calculated_hash = generate_hash(data)
	return calculated_hash == expected_hash