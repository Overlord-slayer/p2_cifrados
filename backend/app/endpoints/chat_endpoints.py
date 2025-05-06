from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.schemas.schemas import *

load_dotenv()

router = APIRouter(prefix="", tags=["chat"])

@router.get("/users/{user}/key")
def get_public_key(user: str):
	return {}

@router.get("/messages/{user_origen}/{user_destino}", response_model=List[str])
def get_messages(user_origen: str, user_destino: str):
	return {}

@router.post("/messages/{user_destino}")
def send_message(user_destino: str, message: str):
	return {}

@router.post("/transactions")
def save_transaction():
	return {}

@router.get("/transactions")
def get_transactions():
	return {}