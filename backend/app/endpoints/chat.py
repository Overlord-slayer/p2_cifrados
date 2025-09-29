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
	try:
		user = db.query(User).filter(User.email == username.strip()).first()
		return user.public_key
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user}/groups")
def api_get_users(user: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		user_sender = get_user_id_by_email(db, user)
		db_groups = get_user_groups(db, user_sender)
		groups = [{"id": group.id} for group in db_groups]
		return groups
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/group-messages/{group_name}/key")
def api_get_group_messages(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		group = db.query(Group).filter(Group.id == group_name.strip()).first()
		return group.shared_aes_key
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/group-messages/create")
def api_create_group(group_name: CreateGroupPayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		user_id = get_user_id_by_email(db, username)
		group = create_group(db, group_name.name, user_id)
		return group.id
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/group-messages/{group_name}/add")
def api_add_to_group(group_name: str, user_destino: CreateGroupPayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		user_receiver = get_user_id_by_email(db, user_destino.name)
		group_user = add_user_to_group(db, user_receiver, group_name)
		return group_user
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/group-messages/{group_name}/owner")
def api_add_to_group(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		owner = get_group_owner_email(db, group_name)
		if owner != username:
			raise HTTPException(status_code=403, detail="Access denied")
		return owner
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/group-messages/{group_name}/users")
def api_add_to_group(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		owner = get_group_owner_email(db, group_name)
		if owner != username:
			raise HTTPException(status_code=403, detail="Access denied")
		non_member_list = get_group_non_participants(db, group_name)
		return non_member_list
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/group-messages/{group_name}", response_model=List[MessageResponse])
def api_get_group_messages(group_name: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		user_sender = get_user_id_by_email(db, username)
		if not user_sender:
			raise HTTPException(status_code=404, detail="Resource not found")

		messages = get_group_messages(db, group_name)
		return messages
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/group-messages/{group_name}")
def api_send_group_message(group_name: str, payload: MessagePayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		user_sender = get_user_id_by_email(db, username)
		if not user_sender:
			raise HTTPException(status_code=404, detail="Resource not found")

		msg = send_group_message(db, user_sender, group_name, payload)

		manager = BlockchainManager(db)
		manager.add_message(False, msg.id)

		return msg
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/messages/{user_origen}/{user_destino}", response_model=List[MessageResponse])
def api_get_messages(user_origen: str, user_destino: str, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		user_sender = get_user_id_by_email(db, user_origen)
		user_receiver = get_user_id_by_email(db, user_destino)
		if not user_sender:
			raise HTTPException(status_code=404, detail="Resource not found")
		if not user_receiver:
			raise HTTPException(status_code=404, detail="Resource not found")

		messages = get_p2p_messages_by_user(db, user_sender, user_receiver)
		return messages
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/messages/{user_destino}")
def api_send_message(user_destino: str, payload: MessagePayload, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		user_sender = get_user_id_by_email(db, username)
		user_receiver = get_user_id_by_email(db, user_destino)
		if not user_sender:
			raise HTTPException(status_code=404, detail="Resource not found")
		if not user_receiver:
			raise HTTPException(status_code=404, detail="Resource not found")

		msg = send_p2p_message(db, user_sender, user_receiver, payload)
		manager = BlockchainManager(db)
		manager.add_message(True, msg.id)

		return msg
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/messages/{user_origen}/{user_destino}/verify-hash")
def api_verify_p2p_hash(user_origen: str, user_destino: str, db: Session = Depends(get_db)):
	try:
		if user_origen == user_destino:
			return False, "Verification skipped"
		user_sender = get_user_id_by_email(db, user_origen)
		user_receiver = get_user_id_by_email(db, user_destino)
		if not user_sender:
			raise HTTPException(status_code=404, detail="Resource not found")
		if not user_receiver:
			raise HTTPException(status_code=404, detail="Resource not found")

		items = get_p2p_messages_by_user(db, user_sender, user_receiver)

		errors = 0
		for item in items:
			if (not verify_hash(item["message"]+item["sender"]+item["receiver"]+item["timestamp"].isoformat(), item["hash"])):
				errors += 1
		if errors > 0:
			return False, "Verification failed"
		return True, "Verification successful"
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/group-messages/{group_name}/verify-hash")
def api_verify_group_hash(group_name: str, db: Session = Depends(get_db)):
	try:
		items = get_group_messages(db, group_name)
		errors = 0
		for item in items:
			if (not verify_hash(item["message"]+item["sender"]+item["receiver"]+item["timestamp"].isoformat(), item["hash"])):
				errors += 1
		if errors > 0:
			return False, "Verification failed"
		return True, "Verification successful"
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/groups/all")
def api_get_all_groups(db: Session = Depends(get_db)):
	groups = db.query(Group).all()
	names = [group.id for group in groups]
	return names

@router.get("/users/all")
def api_get_all_users(db: Session = Depends(get_db)):
	users = db.query(User).all()
	emails = [user.email for user in users]
	return emails
