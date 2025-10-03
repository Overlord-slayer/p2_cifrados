# Importación de llaves y algoritmos de firma
from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import pkcs1_15, DSS
from Crypto.Hash import SHA256
import base64

# Importación de funciones auxiliares para codificación
from .crypto import str_to_bytes, bytes_to_str

# 🖊️ Firmar datos usando RSA y SHA-256
def sign_data(data: str, private_key_pem: bytes) -> str:
    # Importa la clave privada RSA desde formato PEM
    private_key = RSA.import_key(private_key_pem)
    
    # Crea un hash del mensaje a firmar
    hash_obj = SHA256.new(data.encode('utf-8'))
    
    # Genera la firma con PKCS#1 v1.5
    signature = pkcs1_15.new(private_key).sign(hash_obj)
    
    # Devuelve la firma codificada en base64 (como string)
    return base64.b64encode(signature).decode('utf-8')

# ✅ Verificar firma RSA
def verify_signature(data: str, signature_b64: str, public_key_pem: bytes) -> bool:
    try:
        # Importa la clave pública RSA
        public_key = RSA.import_key(public_key_pem)
        
        # Calcula el hash del mensaje original
        hash_obj = SHA256.new(data.encode('utf-8'))
        
        # Decodifica la firma desde base64
        signature = base64.b64decode(signature_b64)
        
        # Verifica que la firma coincida con el mensaje
        pkcs1_15.new(public_key).verify(hash_obj, signature)
        return True
    except Exception as e:
        # Si falla la verificación, imprime el error y devuelve False
        print("\n" + "-"*20 + "Signature" + "-"*21 + "\n" + str(e) + "\n" + "-"*50)
        return False

# 🖊️ Firmar datos usando ECDSA (curvas elípticas)
# Esta versión espera la clave en bytes (formato DER)
def sign_data_ecdsa(data: str, private_key_pem: bytes) -> str:
    private_key_pem = str_to_bytes(private_key_pem)
    private_key = ECC.import_key(private_key_pem)
    
    # Se usa el mismo hash que RSA: SHA-256
    hash_obj = SHA256.new(str_to_bytes(data))
    
    # Crea el firmador según el estándar FIPS 186-3
    signer = DSS.new(private_key, 'fips-186-3')
    
    # Firma el hash y lo retorna en base64
    signature = signer.sign(hash_obj)
    return bytes_to_str(signature)

# 🖊️ Otra versión para firmar datos con ECDSA (clave en string PEM)
def sign_data_ecdsa(data: str, private_key_pem: str) -> str:
    # Importa clave ECC (curva elíptica)
    private_key = ECC.import_key(private_key_pem)
    
    # Crea hash del mensaje
    hash_obj = SHA256.new(data.encode('utf-8'))
    
    # Usa DSS con estándar FIPS
    signer = DSS.new(private_key, 'fips-186-3')
    
    # Firma el mensaje y retorna como base64
    signature = signer.sign(hash_obj)
    return bytes_to_str(signature)

# ✅ Verificar firma con ECDSA (clave pública)
def verify_signature_ecdsa(data: str, signature_b64: str, public_key_pem: str) -> bool:
    try:
        # Importa la clave pública ECC
        public_key = ECC.import_key(public_key_pem)
        
        # Hash del mensaje original
        hash_obj = SHA256.new(data.encode('utf-8'))
        
        # Decodifica la firma desde base64
        signature = str_to_bytes(signature_b64)
        
        # Verifica si la firma es válida
        verifier = DSS.new(public_key, 'fips-186-3')
        verifier.verify(hash_obj, signature)
        return True
    except Exception as e:
        # Imprime error y devuelve False si no pasa la verificación
        print("\n" + "-"*20 + "Signature" + "-"*21 + "\n" + str(e) + "\n" + "-"*50)
        return False
