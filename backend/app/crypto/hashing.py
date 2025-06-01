from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend

def generate_hash(data: str) -> str:
	digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
	digest.update(data.encode('utf-8'))
	return digest.finalize().hex()

def verify_hash(data: str, expected_hash: str) -> bool:
	calculated_hash = generate_hash(data)
	return calculated_hash == expected_hash