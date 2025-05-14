from sqlalchemy.orm import Session
from sqlalchemy import *
from app.db.db import *

def get_user_id_by_email(db: Session, email: str) -> int | None:
	user = db.query(User).filter(User.email == email).first()
	return user.id if user else None

def send_p2p_message(db: Session, sender_id: int, receiver_id: int, message: str):
	msg = P2P_Message(sender_id=sender_id, receiver_id=receiver_id, message=message)
	db.add(msg)
	db.commit()
	db.refresh(msg)
	return msg

def get_p2p_messages_by_user(db: Session, sender_id: int, receiver_id: int):
	return db.query(P2P_Message).filter((P2P_Message.sender_id == sender_id) | (P2P_Message.receiver_id == receiver_id)).order_by(P2P_Message.timestamp.desc()).all()

def add_user_to_group(db: Session, user_id: int, group_id: int):
	membership = GroupMembership(user_id=user_id, group_id=group_id)
	db.add(membership)
	db.commit()
	db.refresh(membership)
	return membership

def get_users_in_group(db: Session, group_id: int):
	return db.query(User).join(GroupMembership).filter(GroupMembership.group_id == group_id).all()

def send_group_message(db: Session, group_id: int, sender_id: int, message: str):
	group_msg = GroupMessage(group_id=group_id, sender_id=sender_id, message=message)
	db.add(group_msg)
	db.commit()
	db.refresh(group_msg)
	return group_msg

def get_messages_in_group(db: Session, group_id: int):
	return db.query(GroupMessage).filter(GroupMessage.group_id == group_id).order_by(GroupMessage.timestamp.asc()).all()