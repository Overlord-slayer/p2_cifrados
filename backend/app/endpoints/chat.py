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

class MessagePayload(BaseModel):
	message: str
	signed: bool

@router.get("/messages/{user_origen}/{user_destino}", response_model=List[str])
def get_messages(user_origen: str, user_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	if user_origen != username:
		raise HTTPException(status_code=404, detail="User denied access")
	if user_destino == "Group Chat":
		user_sender = get_user_id_by_email(db, username)
		if not user_sender:
			raise HTTPException(status_code=404, detail="User not found")

		messages = get_messages_in_group(db)
		return messages

	else:
		user_sender = get_user_id_by_email(db, username)
		user_receiver = get_user_id_by_email(db, user_destino)
		if not user_sender or not user_receiver:
			raise HTTPException(status_code=404, detail="User not found")

		messages = get_p2p_messages_by_user(db, user_sender, user_receiver)
		return messages

@router.post("/messages/{user_destino}")
def send_message(user_destino: str, payload: MessagePayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	if user_destino == "Group Chat":
		sender = get_user_id_by_email(db, username)
		if not sender:
			raise HTTPException(status_code=404, detail="User not found")

		msg = send_group_message(db, sender, payload.message)
		return msg

	else:
		sender = get_user_id_by_email(db, username)
		receiver = get_user_id_by_email(db, user_destino)
		if not sender or not receiver:
			raise HTTPException(status_code=404, detail="User not found")

		msg = send_p2p_message(db, sender, receiver, payload.message)
		return msg