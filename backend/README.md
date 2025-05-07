# Chat App Backend (FastAPI + SQLAlchemy + Auth)

Este proyecto es el backend de una aplicación de chat, construido con FastAPI, autenticación segura y cifrado avanzado.

---

## Requisitos Previos

* Python 3.11 o superior
* pip
* Git (opcional)
* Docker
* Postgres

---

## 1. Levantar docker Compose

```cmd
docker compose up -d
```

##### En Caso de tener postgres localmente, no es necesario levantar el docker.

##### Utilizando docker compose, se ingres las credenciales de adming@admin.com -> admin
![alt text](image.png)

![alt text](image-1.png)


## ⚙️ 1. Crear entorno virtual

### 🔹 En Linux/macOS:
```bash
python3 -m venv env
source env/bin/activate
```

### 🔹 En Windows (CMD):

```cmd
python -m venv env
env\Scripts\activate
```

> En PowerShell: `.\env\Scripts\Activate.ps1` (asegúrate de tener permisos con `Set-ExecutionPolicy` si da error)

---

## 2. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

---

## 3. Correr el backend

```bash
uvicorn app.main:app --reload --log-level debug
```

Esto inicia el servidor en `http://127.0.0.1:8000`

---

## 4. Explicación de dependencias

| Librería                                             | Uso                                                    |
| ---------------------------------------------------- | ------------------------------------------------------ |
| `fastapi`                                            | Framework principal del backend                        |
| `uvicorn`                                            | Servidor ASGI para ejecutar FastAPI                    |
| `SQLAlchemy`                                         | ORM para manejo de base de datos relacional            |
| `psycopg2-binary`                                    | Driver para PostgreSQL                                 |
| `python-dotenv`                                      | Cargar variables desde `.env`                          |
| `passlib`                                            | Hasheo de contraseñas (`bcrypt`, `argon2`)             |
| `bcrypt`                                             | Algoritmo seguro de hash para contraseñas              |
| `python-jose`                                        | Firmado/verificación de JWT                            |
| `pyotp`                                              | Autenticación TOTP (2FA)                               |
| `qrcode`                                             | Generación de códigos QR para TOTP                     |
| `python-multipart`                                   | Soporte para formularios con archivos                  |
| `cryptography`                                       | Utilidades de cifrado modernas (RSA, ECC)              |
| `pycryptodome`, `rsa`, `ecdsa`                       | Cifrado y firma digital personalizada                  |
| `libnacl`, `PyNaCl`                                  | Soporte para cifrado NaCl (usado en Signal, etc)       |
| `email_validator`                                    | Validación de correos electrónicos                     |
| `httpx`, `httpcore`, `h11`                           | Cliente HTTP asíncrono (uso interno FastAPI o Authlib) |
| `Authlib`                                            | Autenticación OAuth 2.0 (Google login)                 |
| `alembic`                                            | Migraciones de base de datos                           |
| `Mako`, `MarkupSafe`                                 | Plantillas de migración usadas por Alembic             |
| `black`, `isort`, `mypy`                             | Herramientas de linting y chequeo estático             |
| `pydantic`, `typing_extensions`, `typing-inspection` | Validación de datos, soporte typing avanzado           |
| `starlette`                                          | Base sobre la que se construye FastAPI                 |

---

## Variables de entorno `.env`

Ejemplo:

```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DATABASE_URL=postgresql://user:password@localhost:5432/chat_db

SECRET_KEY=
SESSION_SECRET_KEY=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
```

---

## Compilar e inicializar

### Crear base de datos (si es necesario):

```bash
python3 `init_db.py` # o python init_db.py en Windows
```

Esto simplemente creara las tablas a la base de datos.

NOTA: ANTES DE HACER ESTO, SE DEBE LEVANTAR EL DOCKER COMPOSE O BIEN TENER INSTALDAO PGADMIN CON POSTGRES.
ASI MISMO, SE DEBE CREAR LA BASE DE DATOS CON NOMBRE chat_app PARA PODER REALIZAR LA CREACION E INSERCION DE DATOS.

---

## Estado

* Autenticación local y por Google 
* 2FA con TOTP y QR 
* Cifrado con RSA/ECC/AES 
* Firma y verificación digital 
* Mini blockchain para registro (opcional) 

---
