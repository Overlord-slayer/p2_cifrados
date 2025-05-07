# Proyecto 2 - Cifrados Seguros

Este proyecto es parte del curso de **Cifrado de Informacion** y tiene como objetivo implementar una aplicación segura que integre mecanismos modernos de **autenticación**, **cifrado**, **firma digital**, **integridad de datos** y **almacenamiento seguro mediante blockchain**. La aplicación incluye funcionalidades de **chat grupal y P2P**, protegidas mediante algoritmos criptográficos.

## Integrantes

| Nombre             | Carné  | Rol                      |
| ------------------ | ------ | ------------------------ |
| Samuel Argueta     | 211024 | Frontend + Autenticación |
| Alejandro Martínez | 21430  | Backend + Chat Grupal    |
| Astrid Glauser     | 21299  | Backend + Chat P2P       |
| Dolan Raúl         | 21965  | Backend + Blockchain     |

## Funcionalidades principales

* Autenticación segura con:
  * OAuth 2.0 con Google
  * TOTP (Two-Factor Authentication)
  * JWT + Refresh Tokens

* Chats protegidos:
  * Chat Grupal con cifrado AES-256-GCM
  * Chat P2P con cifrado de extremo a extremo (X3DH + Double Ratchet)

* Firma Digital con ECDSA
* Verificación de integridad con SHA-256/SHA-3
* Registro de mensajes en una mini Blockchain

## Estructura del proyecto

Este es un monorepo con la siguiente estructura principal:

```
proyecto-cifrados/
├── backend/      # API en FastAPI con toda la lógica criptográfica y autenticación
├── frontend/     # Aplicación web desarrollada en React (Vite)
```

## Tecnologías utilizadas

### Backend (FastAPI)

* **FastAPI**: Framework principal para la API REST.
* **OAuthlib / Authlib**: Implementación del flujo OAuth 2.0 con Google.
* **pyotp**: Generación y verificación de códigos TOTP.
* **PyJWT**: Manejo de Access y Refresh Tokens con JWT.
* **Cryptography**: Firma digital (ECDSA), integridad (SHA-256/SHA-3), y cifrado.
* **PyNaCl**: Cifrado P2P con X3DH y Double Ratchet.
* **PostgreSQL + SQLAlchemy**: Base de datos y ORM para persistencia de usuarios, claves y registros.
* **Docker**: Contenedor para base de datos.

### Frontend (React + Vite)

* **React**: Framework SPA para construir la interfaz del usuario.
* **Vite**: Empaquetador moderno y rápido para desarrollo local.
* **react-router-dom**: Manejo de rutas públicas y protegidas.
* **CSS Modules**: Estilos encapsulados por componente.
* **Hooks personalizados (`useAuth`)**: Manejo del estado de autenticación, sesión, y tokens.
* **Interfaz para Google OAuth 2.0**: Botón de login y manejo del flujo de redirección.
* **Configuración de TOTP**: Visualización de QR y campo para ingresar el código 2FA.

## Flujos de autenticación soportados

| Método               | Tipo de Autenticación | Usa OAuth 2.0 | Usa TOTP   | Tokens JWT |
| -------------------- | --------------------- | ------------- | ---------- | ---------- |
| Email + Contraseña   | Local                 | ❌             | ✅ Opcional | ✅          |
| Google Login (OAuth) | Externo (OAuth 2.0)   | ✅             | ✅ Opcional | ✅          |

> En ambos casos, el backend unifica el flujo generando los tokens JWT y refresh, y permite asociar un secreto TOTP por usuario.
Algo a resltar, que se puede llegar a implementar, es el tema de MFA con google, pero es un veremos.

---

## Instalación y ejecución local

### Requisitos previos

* Docker y Docker Compose
* Node.js (v18 o superior recomendado)
* Python 3.11+

### Backend (FastAPI)

```bash
cd backend
python -m venv env
source env/bin/activate  # o .\env\Scripts\activate en Windows
pip install -r requirements.txt

# Configura las variables de entorno (puedes usar .env)
# Ejecuta el servidor
uvicorn app.main:app --reload
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

### Ejecución con Docker

```bash
# Desde la raíz de la carpeta backend
docker-compose up --build
```

Esto levantará la base de datos PostgreSQL. ESTO SOLO ES NECESARIO SI NO SE TIENE POSTGRES NI PGADMIN INSTALADOS LOCALMENTE.

---

## Variables de entorno necesarias (.env ejemplo)

Definir las siguientes variables de entorno en un archivo `.env` en el backend para que no hayan errores:

```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DATABASE_URL=

SECRET_KEY=
SESSION_SECRET_KEY=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
```

