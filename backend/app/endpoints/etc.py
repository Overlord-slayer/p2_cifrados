from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from typing import *

from app.auth.dependencies import get_current_user
from app.schemas.schemas import *

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.db import get_db
from app.model.models import *

load_dotenv()

router = APIRouter(prefix="", tags=["chat"])

@router.get("/users")
def get_public_key(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	users = db.query(User).all()
	emails = [{"email": user.email} for user in users]
	return emails

@router.get("/users/{user}/key")
def get_public_key(username: str = Depends(get_current_user)):
	return {}

import app.globals as globals

@router.post("/transactions")
def save_transaction(user_destino: str, message: str, username: str = Depends(get_current_user)):
	globals.block_chain.add_transaction(username, user_destino, message)
	return { }

@router.get("/transactions")
def get_transactions(username: str = Depends(get_current_user)):
	return { "transactions" : globals.block_chain.get_all_transactions() }