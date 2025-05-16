import requests

url = "http://127.0.0.1:8000/transactions"
payload = {
    "nombre": "Samuel",
    "fecha_envio": "2025-05-15T19:00:00Z",
    "data_enviada": {"mensaje": "3er bloque de mensajes de prueba"}
}

response = requests.post(url, json=payload)
print(response.status_code)  # 200
print(response.json())       # Bloque creado
