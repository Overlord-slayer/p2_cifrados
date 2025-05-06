from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa

# --- Sign a file using RSA Private Key ---
def sign_data(data: bytes, private_key: rsa.RSAPrivateKey):
	return private_key.sign(data, ec.ECDSA(hashes.SHA256()))

# --- RSA Signature Verification ---
def verify_signature(data: bytes, signature: bytes, public_key: rsa.RSAPublicKey):
	try:
		public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
		return True
	except:
		return False