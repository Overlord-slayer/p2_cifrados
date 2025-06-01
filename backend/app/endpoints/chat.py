from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from typing import *

from app.auth.dependencies import get_current_user
from app.schemas.schemas import *

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.db import get_db
from app.model.models import *

from .chain import *

load_dotenv()

router = APIRouter(prefix="", tags=["chat"])

@router.get("/user")
def api_get_users(username: str = Depends(get_current_user)):
	return username

@router.get("/users")
def api_get_users(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	users = db.query(User).all()
	emails = [{"id": user.email} for user in users]
	return emails

@router.get("/users/{user}/key")
def api_get_public_key(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user = db.query(User).filter(User.email == username.strip()).first()
	return user.public_key

@router.get("/users/{user}/groups")
def api_get_users(user: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, user)
	db_groups = get_user_groups(db, user_sender)
	groups = [{"id": group.id} for group in db_groups]
	return groups

@router.get("/group-messages/{group_name}/key")
def api_get_group_messages(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	group = db.query(Group).filter(Group.id == group_name.strip()).first()
	return group.shared_aes_key

@router.post("/group-messages/create")
def api_create_group(group_name: CreateGroupPayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_id = get_user_id_by_email(db, username)
	group = create_group(db, group_name.name, user_id)
	return group.id

@router.post("/group-messages/{group_name}/add")
def api_add_to_group(group_name: str, user_destino: CreateGroupPayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_receiver = get_user_id_by_email(db, user_destino.name)
	group_user = add_user_to_group(db, user_receiver, group_name)
	return group_user

@router.get("/group-messages/{group_name}/owner")
def api_add_to_group(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	owner = get_group_owner_email(db, group_name)
	if owner != username:
		raise HTTPException(status_code=403, detail=f"You are not the owner, this is: {owner}")
	return owner

@router.get("/group-messages/{group_name}/users")
def api_add_to_group(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	owner = get_group_owner_email(db, group_name)
	if owner != username:
		raise HTTPException(status_code=403, detail=f"You are not the owner, this is: {owner}")
	non_member_list = get_group_non_participants(db, group_name)
	return non_member_list

@router.get("/group-messages/{group_name}", response_model=List[MessageResponse])
def api_get_group_messages(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, username)
	if not user_sender:
		raise HTTPException(status_code=404, detail=f"User not found: {user_sender}")

	messages = get_group_messages(db, group_name)
	return messages

@router.post("/group-messages/{group_name}")
def api_send_group_message(group_name: str, payload: MessagePayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, username)
	if not user_sender:
		raise HTTPException(status_code=404, detail=f"User not found: {user_sender}")

	msg = send_group_message(db, user_sender, group_name, payload)

	manager = BlockchainManager(db)
	manager.add_message(False, msg.id)

	return msg

@router.get("/messages/{user_origen}/{user_destino}", response_model=List[MessageResponse])
def api_get_messages(user_origen: str, user_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, user_origen)
	user_receiver = get_user_id_by_email(db, user_destino)
	if not user_sender:
		raise HTTPException(status_code=404, detail=f"User not found: {user_sender}")
	if not user_receiver:
		raise HTTPException(status_code=404, detail=f"User not found: {user_receiver}")

	messages = get_p2p_messages_by_user(db, user_sender, user_receiver)
	return messages

@router.post("/messages/{user_destino}")
def api_send_message(user_destino: str, payload: MessagePayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, username)
	user_receiver = get_user_id_by_email(db, user_destino)
	if not user_sender:
		raise HTTPException(status_code=404, detail=f"User not found: {user_sender}")
	if not user_receiver:
		raise HTTPException(status_code=404, detail=f"User not found: {user_receiver}")

	msg = send_p2p_message(db, user_sender, user_receiver, payload)
	manager = BlockchainManager(db)
	manager.add_message(True, msg.id)

	return msg

@router.post("/messages/{user_origen}/{user_destino}/verify-hash")
def api_verify_p2p_hash(user_origen: str, user_destino: str, db: Session = Depends(get_db)):
	user_sender = get_user_id_by_email(db, user_origen)
	user_receiver = get_user_id_by_email(db, user_destino)
	if not user_sender:
		raise HTTPException(status_code=404, detail=f"User not found: {user_origen}")
	if not user_receiver:
		raise HTTPException(status_code=404, detail=f"User not found: {user_destino}")

	items = get_p2p_messages_by_user(db, user_sender, user_receiver)
	messages = [item["message"] for item in items]
	hashes = [item["hash"] for item in items]

	errors = 0
	for message, hash in zip(messages, hashes):
		if (not verify_hash(message, hash)):
			errors += 1
	if errors > 0:
		return False, f"Hashing failed for {errors}/{len(items)} items."
	return True, f"Hashes verified for {len(items)} items."

@router.post("/group-messages/{group_name}/verify-hash")
def api_verify_group_hash(group_name: str, db: Session = Depends(get_db)):
	items = get_group_messages(db, group_name)
	messages = [item["message"] for item in items]
	hashes = [item["hash"] for item in items]

	errors = 0
	for message, hash in zip(messages, hashes):
		if (not verify_hash(message, hash)):
			errors += 1
	if errors > 0:
		return False, f"Hashing failed for {errors}/{len(items)} items."
	return True, f"Hashes verified for {len(items)} items."