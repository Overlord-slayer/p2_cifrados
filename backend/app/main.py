from fastapi import FastAPI
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logger import RequestLoggerMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

from app.auth.google.routes import router as google_login_router
from app.auth.google.callback import router as google_callback_router
from app.endpoints.group_chat import router as group_chat_router
from app.endpoints.p2p_chat import router as p2p_chat_router
from app.endpoints.etc import router as etc_chat_router

from dotenv import load_dotenv

import app.globals as globals

load_dotenv()

app = FastAPI()

@app.on_event("startup")
async def on_startup():
	print("App is starting up...")

@app.on_event("shutdown")
async def on_shutdown():
	print("App is shutting down...")

app.include_router(etc_chat_router)
app.include_router(p2p_chat_router)
app.include_router(group_chat_router)
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