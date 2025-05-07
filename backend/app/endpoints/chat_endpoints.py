from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from typing import *

from app.auth.dependencies import get_current_user
from app.schemas.schemas import *

import app.globals as globals
from app.db.db import *

load_dotenv()

router = APIRouter(prefix="", tags=["chat"])

@router.get("/users/{user}/key")
def get_public_key(username: str = Depends(get_current_user)):
	return {}

@router.get("/messages/{user_origen}/{user_destino}", response_model=List[str])
def get_messages(user_destino: str, username: str = Depends(get_current_user)):
	return {}

@router.post("/messages/{user_destino}")
def send_message(user_destino: str, message: str, username: str = Depends(get_current_user)):
	db = get_db()
	return {}

@router.post("/transactions")
def save_transaction(user_destino: str, message: str, username: str = Depends(get_current_user)):
	globals.block_chain.add_transaction(username, user_destino, message)
	return { }

@router.get("/transactions")
def get_transactions(username: str = Depends(get_current_user)):
	return { "transactions" : globals.block_chain.get_all_transactions() }