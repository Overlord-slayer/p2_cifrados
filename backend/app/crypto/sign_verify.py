from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import padding

# --- Sign a file using RSA Private Key ---
def sign_data(data: bytes, private_key):
	# Sign the file data using ECDSA with SHA-256
	signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))

	return signature

# --- RSA Signature Verification ---
def verify_signature(data: bytes, signature: bytes, public_key):
	try:
		# Verify the signature using ECDSA with SHA-256
		public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
		return True
	except Exception as e:
		# If the signature is invalid, an exception is raised
		return False