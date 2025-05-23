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
def api_get_users(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	users = db.query(User).all()
	emails = [{"id": user.email} for user in users]
	return emails

@router.get("/users/{user}/key")
def api_get_public_key(username: str = Depends(get_current_user)):
	return {}

@router.get("/users/{user}/groups")
def api_get_users(user: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, user)
	db_groups = get_user_groups(db, user_sender)
	groups = [{"id": group.id} for group in db_groups]
	return groups

class CreateGroupPayload(BaseModel):
	name: str

@router.post("/group-messages/create")
def api_create_group(group_name: CreateGroupPayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	group = create_group(db, group_name.name)
	return group.id

@router.post("/group-messages/{group_name}/add")
def api_add_to_group(group_name: str, user_destino: CreateGroupPayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_receiver = get_user_id_by_email(db, user_destino.name)
	group_user = add_user_to_group(db, user_receiver, group_name)
	return group_user

class MessagePayload(BaseModel):
	message: str
	signed: bool

class MessageResponse(BaseModel):
	sender_id: int
	receiver_id: str
	message: str
	signature: Optional[str] = None
	timestamp: datetime

@router.get("/group-messages/{group_name}", response_model=List[MessageResponse])
def api_get_group_messages(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, username)
	if not user_sender:
		raise HTTPException(status_code=404, detail="User not found")

	db_messages = get_group_messages(db, group_name)
	messages = [{
		"sender_id": msg.sender_id,
		"receiver_id": msg.group_name,
		"message": msg.message,
		"signature": None,
		"timestamp": msg.timestamp,
	} for msg in db_messages]
	return messages

@router.post("/group-messages/{group_name}")
def api_send_group_message(group_name: str, payload: MessagePayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	sender = get_user_id_by_email(db, username)
	if not sender:
		raise HTTPException(status_code=404, detail="User not found")

	msg = send_group_message(db, sender, group_name, payload.message)
	return msg

@router.get("/messages/{user_origen}/{user_destino}", response_model=List[str])
def api_get_messages(user_origen: str, user_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, username)
	user_receiver = get_user_id_by_email(db, user_destino)
	if not user_sender or not user_receiver:
		raise HTTPException(status_code=404, detail="User not found")

	messages = get_p2p_messages_by_user(db, user_sender, user_receiver)
	return messages

@router.post("/messages/{user_destino}")
def api_send_message(user_destino: str, payload: MessagePayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	sender = get_user_id_by_email(db, username)
	receiver = get_user_id_by_email(db, user_destino)
	if not sender or not receiver:
		raise HTTPException(status_code=404, detail="User not found")

	msg = send_p2p_message(db, sender, receiver, payload.message)
	return msg