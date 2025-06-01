from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

def sign_data(data: str, private_key_pem: bytes) -> str:
	private_key = RSA.import_key(private_key_pem)
	hash_obj = SHA256.new(data.encode('utf-8'))
	signature = pkcs1_15.new(private_key).sign(hash_obj)
	return base64.b64encode(signature).decode('utf-8')

def verify_signature(data: str, signature_b64: str, public_key_pem: bytes) -> bool:
	try:
		public_key = RSA.import_key(public_key_pem)
		hash_obj = SHA256.new(data.encode('utf-8'))
		signature = base64.b64decode(signature_b64)
		pkcs1_15.new(public_key).verify(hash_obj, signature)
		return True
	except (ValueError, TypeError):
		return False