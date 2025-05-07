from sqlalchemy.orm import Session
from sqlalchemy import *
from app.db.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False)
	totp_secret = Column(String, nullable=True)
	public_key = Column(
		LargeBinary, nullable=True
	)  # ECC/RSA pública para cifrado o firma
	is_active = Column(Boolean, default=True)

	# Nuevos campos
	is_google_account = Column(
		Boolean, default=False
	)  # Indica si el usuario usó Google
	email_verified = Column(
		Boolean, default=False
	)  # Por si quieres manejar verificación
	totp_verified = Column(Boolean, default=False)  # True después de escanear QR

class P2P_Message(Base):
	__tablename__ = "p2p_messages"

	id = Column(Integer, primary_key=True, index=True)
	
	sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	
	message = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	# Relationships to link to User
	sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
	receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")

class Group(Base):
	__tablename__ = "groups"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

class GroupMembership(Base):
	__tablename__ = "group_memberships"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
	joined_at = Column(DateTime, default=datetime.utcnow)

	user = relationship("User", backref="group_memberships")
	group = relationship("Group", backref="memberships")

class GroupMessage(Base):
	__tablename__ = "group_messages"

	id = Column(Integer, primary_key=True, index=True)
	group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
	sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	message = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	group = relationship("Group", backref="messages")
	sender = relationship("User", backref="group_messages")

def send_p2p_message(db: Session, sender_id: int, receiver_id: int, message: str):
	msg = P2P_Message(sender_id=sender_id, receiver_id=receiver_id, message=message)
	db.add(msg)
	db.commit()
	db.refresh(msg)
	return msg

def get_p2p_messages_by_user(db: Session, user_id: int):
	return db.query(P2P_Message).filter(
		(P2P_Message.sender_id == user_id) | (P2P_Message.receiver_id == user_id)
	).order_by(P2P_Message.timestamp.desc()).all()

def add_user_to_group(db: Session, user_id: int, group_id: int):
	membership = GroupMembership(user_id=user_id, group_id=group_id)
	db.add(membership)
	db.commit()
	db.refresh(membership)
	return membership

def get_groups_for_user(db: Session, user_id: int):
	return db.query(Group).join(GroupMembership).filter(GroupMembership.user_id == user_id).all()

def send_group_message(db: Session, group_id: int, sender_id: int, message: str):
	group_msg = GroupMessage(group_id=group_id, sender_id=sender_id, message=message)
	db.add(group_msg)
	db.commit()
	db.refresh(group_msg)
	return group_msg

def get_messages_in_group(db: Session, group_id: int):
	return db.query(GroupMessage).filter(GroupMessage.group_id == group_id).order_by(GroupMessage.timestamp.asc()).all()
