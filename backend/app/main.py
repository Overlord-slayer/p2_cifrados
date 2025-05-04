from fastapi import FastAPI
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logger import LoggingMiddleware

app = FastAPI()

app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # O "*" si estás probando
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
