from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# --- Sign a file using RSA Private Key ---
def sign_file(file_path: str, private_key):
	# Read file data
	with open(file_path, 'rb') as f:
		file_data = f.read()

	# Sign the file data
	signature = private_key.sign(
		file_data,
		padding.PKCS1v15(),
		hashes.SHA256()
	)

	return signature

# --- RSA Signature Verification ---
def verify_signature(file_path: str, signature: bytes, public_key):
	# Read file data
	with open(file_path, 'rb') as f:
		file_data = f.read()

	try:
		# Verify the signature
		public_key.verify(
			signature,
			file_data,
			padding.PKCS1v15(),
			hashes.SHA256()
		)
		return True
	except Exception as e:
		# If the signature is invalid, an exception is raised
		return False