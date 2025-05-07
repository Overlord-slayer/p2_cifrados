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

@router.get("/messages/{user_origen}/{user_destino}", response_model=List[str])
def get_messages(user_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	get_p2p_messages_by_user(db, username)
	return {}

@router.post("/messages/{user_destino}")
def send_message(user_destino: str, message: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	send_p2p_message(db, username, get_user_id_by_email(user_destino), message)
	return {}