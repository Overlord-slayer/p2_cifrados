from sqlalchemy.orm import Session
from sqlalchemy import *
from app.db.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship

from app.crypto.crypto import *

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

	id = Column(String, primary_key=True, index=True)

	shared_aes_key = Column(String, nullable=False)

	users = relationship("GroupUser", back_populates="group", cascade="all, delete-orphan")
	messages = relationship("GroupMessage", back_populates="group", cascade="all, delete-orphan")

class GroupUser(Base):
	__tablename__ = "group_users"

	id = Column(Integer, primary_key=True, index=True)

	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	group_name = Column(String, ForeignKey("groups.id"), nullable=False)

	user = relationship("User", backref="group_memberships")
	group = relationship("Group", back_populates="users")

class GroupMessage(Base):
	__tablename__ = "group_messages"

	id = Column(Integer, primary_key=True, index=True)

	sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	group_name  = Column(String, ForeignKey("groups.id"), nullable=False)

	message = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	sender = relationship("User", foreign_keys=[sender_id], backref="sent_group_messages")
	group = relationship("Group", foreign_keys=[group_name], backref="group_data")

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

def add_user_to_group(db: Session, user_id: int, group_name: int):
	existing = db.query(GroupUser).filter_by(user_id=user_id, group_name=group_name).first()
	if existing:
		return existing
	group_user = GroupUser(user_id=user_id, group_name=group_name)
	db.add(group_user)
	db.commit()
	db.refresh(group_user)
	return group_user

def send_group_message(db: Session, sender_id: int, group_name: int, message: str):
	group_message = GroupMessage(
		sender_id=sender_id,
		group_name=group_name,
		message=message
	)
	db.add(group_message)
	db.commit()
	db.refresh(group_message)
	return group_message

def get_group_messages(db: Session, group_name: int, limit: int = 100):
	return (
		db.query(GroupMessage)
		.filter_by(group_name=group_name)
		.order_by(GroupMessage.timestamp.desc())
		.limit(limit)
		.all()
	)

def get_user_groups(db: Session, user_id: int):
	return (
		db.query(Group)
		.join(GroupUser)
		.filter(GroupUser.user_id == user_id)
		.all()
	)

def create_group(db: Session, name: str) -> Group:
	new_group = Group(name=name, shared_aes_key=base64_bytes_to_string(get_random_bytes(32)))
	db.add(new_group)
	db.commit()
	db.refresh(new_group)
	return new_group