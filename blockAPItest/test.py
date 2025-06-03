import requests
import datetime
import json

BASE_URL = "http://localhost:8000"

def crear_transaccion():
    url = f"{BASE_URL}/transactions"
    data = {
        "nombre": "Teest",
        "fecha_envio": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "data_enviada": 
               {
            "mensaje": "Bloque de prueba con datos 2"}
    }
    response = requests.post(url, json=data)
    print("Crear Transacción:")
    print("Status Code:", response.status_code)
    print(json.dumps(response.json(), indent=4))

def obtener_todos_los_bloques():
    url = f"{BASE_URL}/transactions"
    response = requests.get(url)
    print("\n Todos los bloques:")
    print("Status Code:", response.status_code)
    for block in response.json():
        print(json.dumps(block, indent=4))

def validar_cadena():
    url = f"{BASE_URL}/validate"
    response = requests.get(url)
    print("\n Validación de la cadena:")
    print("Status Code:", response.status_code)
    print("¿Cadena válida?:", response.json()["chain_valid"])

def obtener_ultimo_bloque():
    url = f"{BASE_URL}/last_block"
    response = requests.get(url)
    print("\n Último bloque:")
    print("Status Code:", response.status_code)
    print(json.dumps(response.json(), indent=4))

if __name__ == "__main__":
    crear_transaccion()
    obtener_todos_los_bloques()
    obtener_ultimo_bloque()
    validar_cadena()
