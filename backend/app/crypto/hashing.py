# Importación de primitivas criptográficas y backend seguro
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend

# 🧮 Función para generar un hash SHA-256 de una cadena
def generate_hash(data: str) -> str:
    # Se crea un objeto Hash utilizando SHA-256 como algoritmo
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    
    # Se alimenta el hash con el contenido de la cadena codificada en UTF-8
    digest.update(data.encode('utf-8'))
    
    # Se obtiene el resultado final en formato hexadecimal
    return digest.finalize().hex()

# ✅ Función para verificar si el hash de un dato coincide con un hash esperado
def verify_hash(data: str, expected_hash: str) -> bool:
    # Calcula el hash actual del dato proporcionado
    calculated_hash = generate_hash(data)
    
    # Compara si el hash calculado coincide exactamente con el esperado
    return calculated_hash == expected_hash
