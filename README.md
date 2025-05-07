# Proyecto 2 - Cifrados Seguros

Este proyecto es parte del curso de **Seguridad Informática** y tiene como objetivo implementar una aplicación segura que integre mecanismos modernos de **autenticación**, **cifrado**, **firma digital**, **integridad de datos** y **almacenamiento seguro mediante blockchain**. La aplicación incluye funcionalidades de **chat grupal y P2P**, protegidas mediante algoritmos criptográficos robustos.

## Integrantes

| Nombre             | Carné  | Rol                      |
| ------------------ | ------ | ------------------------ |
| Samuel Argueta     | 211024 | Frontend + Autenticación |
| Alejandro Martínez | 21430  | Backend + Chat Grupal    |
| Astrid Glauser     | 21299  | Backend + Chat P2P       |
| Dolan Raúl         | 21965  | Backend + Blockchain     |

## Funcionalidades principales

* Autenticación segura con:
  * OAuth 2.0
  * TOTP (Two-Factor Authentication)
  * JWT + Refresh Tokens

* Chats protegidos:
  * Chat Grupal con cifrado AES-256-GCM
  * Chat P2P con cifrado de extremo a extremo (X3DH + Double Ratchet)

* Firma Digital con ECDSA
* Verificación de integridad con SHA-256/SHA-3
* Registro de mensajes en una mini Blockchain

## Tecnologías utilizadas

* **Frontend**: React + Vite + CSS Modules
* **Backend**: FastAPI + PostgreSQL + sqlAlchemist + OAuthlib
* **Criptografía**: pyca/cryptography, PyNaCl, pyotp
* **Blockchain**: Implementación propia en Python
* **Contenedores**: Docker + Docker Compose
>>>>>>> 0d1e010de1938e024063c8e56932266d3237f5b3
