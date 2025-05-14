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

@router.get("/messages/{user_origen}/{user_destino}", response_model=List[str])
def get_messages(user_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = db.query(User).filter(User.username == username).first()
	user_receiver = db.query(User).filter(User.username == user_destino).first()
	if not user_sender or not user_receiver:
		raise HTTPException(status_code=404, detail="User not found")

	messages = get_p2p_messages_by_user(db, user_sender.id, user_receiver.id)
	return messages

@router.post("/messages/{user_destino}")
def send_message(user_destino: str, message: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	sender = get_user_id_by_email(username).first()
	receiver = get_user_id_by_email(user_destino).first()
	if not sender or not receiver:
		raise HTTPException(status_code=404, detail="User not found")

	msg = send_p2p_message(db, sender.id, receiver.id, message)
	return msg