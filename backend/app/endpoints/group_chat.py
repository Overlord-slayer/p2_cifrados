from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from typing import *

from app.auth.dependencies import get_current_user
from app.schemas.schemas import *

from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.db import get_db
from app.model.models import *

load_dotenv()

router = APIRouter(prefix="", tags=["chat"])

@router.get("/group/messages/{grupo_destino}", response_model=List[str])
def get_messages(grupo_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	get_messages_in_group(db, grupo_destino)
	return {}

@router.post("/group/messages/{grupo_destino}")
def send_message(grupo_destino: str, message: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	send_group_message(db, grupo_destino, username, message)
	return {}

@router.get("/groups/users/{grupo_destino}", response_model=List[str])
def get_messages(grupo_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	get_users_in_group(db, grupo_destino)
	return {}

@router.post("/group/users/{grupo_destino}")
def add_to_group(grupo_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	add_user_to_group(db, username, grupo_destino)
	return {}