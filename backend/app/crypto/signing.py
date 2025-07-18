from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import pkcs1_15, DSS
from Crypto.Hash import SHA256
import base64

from.crypto import str_to_bytes, bytes_to_str

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
	except Exception as e:
		print("\n"+"-"*20+"Signature"+"-"*21+"\n"+str(e)+"\n"+"-"*50)
		return False

def sign_data_ecdsa(data: str, private_key_pem: bytes) -> str:
	private_key_pem = str_to_bytes(private_key_pem)
	private_key = ECC.import_key(private_key_pem)
	hash_obj = SHA256.new(str_to_bytes(data))
	signer = DSS.new(private_key, 'fips-186-3')
	signature = signer.sign(hash_obj)
	return bytes_to_str(signature)

def sign_data_ecdsa(data: str, private_key_pem: str) -> str:
	private_key = ECC.import_key(private_key_pem)
	hash_obj = SHA256.new(data.encode('utf-8'))
	signer = DSS.new(private_key, 'fips-186-3')
	signature = signer.sign(hash_obj)
	return bytes_to_str(signature)

def verify_signature_ecdsa(data: str, signature_b64: str, public_key_pem: str) -> bool:
	try:
		public_key = ECC.import_key(public_key_pem)
		hash_obj = SHA256.new(data.encode('utf-8'))
		signature = str_to_bytes(signature_b64)
		verifier = DSS.new(public_key, 'fips-186-3')
		verifier.verify(hash_obj, signature)
		return True
	except Exception as e:
		print("\n"+"-"*20+"Signature"+"-"*21+"\n"+str(e)+"\n"+"-"*50)
		return False