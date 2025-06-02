from fastapi import FastAPI
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logger import RequestLoggerMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

from app.auth.google.routes import router as google_login_router
from app.auth.google.callback import router as google_callback_router
from app.endpoints.chat import router as chat_router

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.on_event("startup")
async def on_startup():
	print("App is starting up...")

@app.on_event("shutdown")
async def on_shutdown():
	print("App is shutting down...")

app.include_router(chat_router)
app.include_router(auth.router)
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