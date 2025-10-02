from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

from app.routers import auth
from app.middleware.logger import RequestLoggerMiddleware
from app.auth.google.routes import router as google_login_router
from app.auth.google.callback import router as google_callback_router
from app.endpoints.chat import router as chat_router
from app.endpoints.chain import router as chain_router

from dotenv import load_dotenv

load_dotenv()

# Middleware de cabeceras de seguridad
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
	"""
	Añade cabeceras de seguridad a todas las respuestas y oculta el header Server.
	"""
	async def dispatch(self, request: Request, call_next):
		response: Response = await call_next(request)
		
		# Ocultar header Server
		if "server" in response.headers:
			del response.headers["server"]
		
		# Cabeceras de seguridad
		response.headers["X-Content-Type-Options"] = "nosniff"
		response.headers["X-Frame-Options"] = "DENY"
		response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
		response.headers["X-XSS-Protection"] = "1; mode=block"
		response.headers["Content-Security-Policy"] = "default-src 'self'"
		
		# HSTS solo en producción (asumiendo HTTPS)
		environment = os.getenv("ENVIRONMENT", "development")
		if environment == "production":
			response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
		
		return response

app = FastAPI()

app.include_router(auth.router)
app.include_router(chat_router)
app.include_router(chain_router)
app.include_router(google_login_router)
app.include_router(google_callback_router)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],  # O "*" si estás probando
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
