from fastapi import FastAPI, Request, Response
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logger import RequestLoggerMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import os

from app.auth.google.routes import router as google_login_router
from app.auth.google.callback import router as google_callback_router
from app.endpoints.chat import router as chat_router
from app.endpoints.chain import router as chain_router

from dotenv import load_dotenv

load_dotenv()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		response = await call_next(request)
		
		# NO toques headers de CORS si ya existen
		cors_headers = {
			"access-control-allow-origin",
			"access-control-allow-credentials", 
			"access-control-allow-headers",
			"access-control-allow-methods",
			"vary",
		}
		
		# Añade tus headers de seguridad sin sobrescribir CORS:
		def setdefault(h, v):
			if h.lower() not in cors_headers and h not in response.headers:
				response.headers[h] = v
		
		setdefault("X-Content-Type-Options", "nosniff")
		setdefault("X-Frame-Options", "DENY") 
		setdefault("X-XSS-Protection", "1; mode=block")
		setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
		setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
		
		# CSP: más permisivo para docs de Swagger
		ct = response.headers.get("content-type", "")
		if "text/html" in ct:
			# Allow CDN resources for Swagger UI
			setdefault("Content-Security-Policy", 
				"default-src 'self'; "
				"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
				"script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
				"img-src 'self' data: https://fastapi.tiangolo.com")
		
		# Ocultar banner del servidor correctamente
		try:
			del response.headers["server"]
		except KeyError:
			pass
		
		return response

# Hide development information in production
app = FastAPI(
	title="API",
	description="",
	version="1.0.0",
	docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
	redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc",
	openapi_url=None if os.getenv("ENVIRONMENT") == "production" else "/openapi.json"
)

app.include_router(auth.router)
app.include_router(chat_router)
app.include_router(chain_router)
app.include_router(google_login_router)
app.include_router(google_callback_router)

# 1) Seguridad primero
app.add_middleware(SecurityHeadersMiddleware)

# 2) Sessions / lo que haga falta
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"), same_site="lax")

# 3) Request logger
app.add_middleware(RequestLoggerMiddleware)

# 4) CORS AL FINAL (para que sea el outermost y no lo pisen luego)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
