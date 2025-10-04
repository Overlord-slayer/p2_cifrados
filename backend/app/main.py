from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.utils.limiter import limiter

import os

from app.routers import auth
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

from app.routers import auth
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
	CSP estricta para la app, relajada solo para /docs y /redoc (Swagger).
	"""
	async def dispatch(self, request: Request, call_next):
		response: Response = await call_next(request)
		
		# Ocultar header Server
		if "server" in response.headers:
			del response.headers["server"]
		
		# Cabeceras de seguridad comunes
		response.headers["X-Content-Type-Options"] = "nosniff"
		response.headers["X-Frame-Options"] = "DENY"
		response.headers["Referrer-Policy"] = "no-referrer"
		
		# CSP: estricta para app, relajada para /docs y /redoc
		path = request.url.path
		if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
			# CSP relajada para Swagger UI (necesita unsafe-inline)
			response.headers["Content-Security-Policy"] = (
				"default-src 'self'; "
				"script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
				"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
				"img-src 'self' data: https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
				"font-src 'self' data: https://cdn.jsdelivr.net; "
				"connect-src 'self'; "
				"object-src 'none'; "
				"base-uri 'self'; "
				"form-action 'self'; "
				"frame-ancestors 'none'; "
				"frame-src 'none'"
			)
		else:
			# CSP estricta para la aplicación (SIN unsafe-inline, unsafe-eval)
			response.headers["Content-Security-Policy"] = (
				"default-src 'self'; "
				"script-src 'self'; "
				"style-src 'self'; "
				"img-src 'self' data:; "
				"font-src 'self' data:; "
				"connect-src 'self'; "
				"object-src 'none'; "
				"base-uri 'self'; "
				"form-action 'self'; "
				"frame-ancestors 'none'; "
				"frame-src 'none'"
			)
		
		return response

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Incluir routers antes de montar StaticFiles
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

# Montar frontend build si existe
dist_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.isdir(dist_path):
	app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
