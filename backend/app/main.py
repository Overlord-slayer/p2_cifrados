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
		
		# Hide server information
		response.headers["Server"] = ""
		response.headers.pop("Server", None)
		
		# Security headers
		response.headers["X-Content-Type-Options"] = "nosniff"
		response.headers["X-Frame-Options"] = "DENY"
		response.headers["X-XSS-Protection"] = "1; mode=block"
		response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
		response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
		response.headers["Content-Security-Policy"] = "default-src 'self'"
		
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

# Add security headers middleware first
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],  # O "*" si estás probando
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.add_middleware(RequestLoggerMiddleware)
