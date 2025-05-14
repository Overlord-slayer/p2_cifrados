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

@router.get("/group/messages/{grupo_destino}", response_model=List[str])
def get_messages(grupo_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	messages = get_messages_in_group(db, grupo_destino)
	return messages

@router.post("/group/messages/{grupo_destino}")
def send_message(grupo_destino: str, message: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user = get_user_id_by_email(username).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")

	new_msg = send_group_message(db, grupo_destino, user.id, message)
	return new_msg

@router.get("/groups/users/{grupo_destino}", response_model=List[str])
def get_messages(grupo_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	users = get_users_in_group(db, grupo_destino)
	return users

@router.post("/group/users/{grupo_destino}")
def add_to_group(grupo_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user = get_user_id_by_email(username).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	membership = add_user_to_group(db, user.id, grupo_destino)
	return user