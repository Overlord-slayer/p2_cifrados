from sqlalchemy.orm import Session
from sqlalchemy import *
from app.db.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship

from app.schemas.schemas import *
from typing import Optional

from app.crypto.crypto import *
from app.crypto.signing import *
from app.crypto.hashing import *

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False)
	totp_secret = Column(String, nullable=True)

	public_key = Column(String, nullable=False)
	private_key = Column(String, nullable=False)
	
	public_ecc_key = Column(String, nullable=False)
	private_ecc_key = Column(String, nullable=False)

	is_active = Column(Boolean, default=True)

	is_google_account = Column(Boolean, default=False)
	email_verified = Column(Boolean, default=False)
	totp_verified = Column(Boolean, default=False)

class P2P_Message(Base):
	__tablename__ = "p2p_messages"

	id = Column(Integer, primary_key=True, index=True)

	sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

	hash = Column(Text, nullable=False)
	signature = Column(Text)
	message = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
	receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")

class Group(Base):
	__tablename__ = "groups"

	id = Column(String, primary_key=True, index=True)
	owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

	shared_aes_key = Column(String, nullable=False)

	owner = relationship("User", backref="owned_groups")
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

	hash = Column(Text, nullable=False)
	message = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	sender = relationship("User", foreign_keys=[sender_id], backref="sent_group_messages")
	group = relationship("Group", foreign_keys=[group_name], backref="group_data")

class Block(Base):
	__tablename__ = "blocks"

	id = Column(Integer, primary_key=True)
	hash = Column(String, unique=True)
	previous_hash = Column(String, nullable=True)
	timestamp = Column(DateTime, default=datetime.utcnow)

	messages = relationship("BlockMessage", back_populates="block")

class BlockMessage(Base):
	__tablename__ = "blockchain_messages"

	id = Column(Integer, primary_key=True)
	is_p2p = Column(Boolean)  # "0" or "1"
	message_id = Column(Integer)  # Reference to either P2P_Message.id or GroupMessage.id

	block_id = Column(Integer, ForeignKey("blocks.id"))
	block = relationship("Block", back_populates="messages")

class CreateGroupPayload(BaseModel):
	name: str

class MessagePayload(BaseModel):
	message: str
	signed: bool

class MessageResponse(BaseModel):
	sender: str
	receiver: str
	message: str
	signature: Optional[str] = None
	hash: str
	timestamp: datetime

def get_user_id_by_email(db: Session, email: str) -> int | None:
	user = db.query(User).filter(User.email == email.strip()).first()
	return user.id if user else None

def get_email_by_user_id(db: Session, id: int) -> int | None:
	user = db.query(User).filter(User.id == id).first()
	return user.email if user else None

def send_p2p_message(db: Session, sender_id: int, receiver_id: int, payload: MessagePayload):
	sender = db.query(User).filter_by(id=sender_id).first()
	receiver = db.query(User).filter_by(id=receiver_id).first()

	pub_key = str_to_bytes(receiver.public_key)
	encrypted_message = cifrar_mensaje_individual(payload.message, pub_key)

	signature = None
	if (payload.signed):
		private_ecc_key_encrypted = str_to_bytes(sender.private_ecc_key)
		private_ecc_key = decrypt_bytes(private_ecc_key_encrypted)
		signature = sign_data_ecdsa(encrypted_message, private_ecc_key)

	msg = P2P_Message(
		sender_id=sender_id,
		receiver_id=receiver_id,
		message=encrypted_message,
		signature=signature,
		hash=generate_hash(payload.message)
	)
	db.add(msg)
	db.commit()
	db.refresh(msg)
	return msg

def get_p2p_messages_by_user(db: Session, user1_id: int, user2_id: int):
	user1_db = db.query(User).filter_by(id=user1_id).first()
	user2_db = db.query(User).filter_by(id=user2_id).first()

	data = db.query(P2P_Message).filter(
		or_(
			and_(P2P_Message.sender_id == user1_id, P2P_Message.receiver_id == user2_id),
			and_(P2P_Message.sender_id == user2_id, P2P_Message.receiver_id == user1_id)
		)
	).order_by(P2P_Message.timestamp.desc()).all()

	messages = []
	for msg in data:
		sender =   user1_db if msg.sender_id   == user1_id else user2_db
		receiver = user2_db if msg.receiver_id == user2_id else user1_db

		private_key_encrypted = str_to_bytes(receiver.private_key)
		private_key = decrypt_bytes(private_key_encrypted)
		decrypted_message = descifrar_mensaje_individual(msg.message, private_key)

		signature = None
		if (msg.signature):
			pub_ecc_key = str_to_bytes(sender.public_ecc_key)
			if (verify_signature_ecdsa(msg.message, msg.signature, pub_ecc_key)):
				signature = "Signed"

		messages.append({
			"sender":    sender.email,
			"receiver":  receiver.email,
			"message" :  decrypted_message,
			"signature": signature,
			"hash": msg.hash,
			"timestamp": msg.timestamp,
		})
	return messages

def add_user_to_group(db: Session, user_id: int, group_name: int):
	existing = db.query(GroupUser).filter_by(user_id=user_id, group_name=group_name).first()
	if existing:
		return existing
	group_user = GroupUser(user_id=user_id, group_name=group_name)
	db.add(group_user)
	db.commit()
	db.refresh(group_user)
	return group_user

def send_group_message(db: Session, sender_id: int, group_name: str, payload: MessagePayload):
	aes_key_string = db.query(Group).filter_by(id=group_name).first().shared_aes_key
	aes_key = str_to_bytes(aes_key_string)
	encrypted_message = cifrar_mensaje_grupal(payload.message, aes_key)

	group_message = GroupMessage(
		sender_id=sender_id,
		group_name=group_name,
		message=encrypted_message,
		hash=generate_hash(payload.message)
	)
	db.add(group_message)
	db.commit()
	db.refresh(group_message)

	result_message = group_message
	result_message.message = payload.message
	return result_message

def get_group_messages(db: Session, group_name: int):
	data = (
		db.query(GroupMessage)
		.filter_by(group_name=group_name)
		.order_by(GroupMessage.timestamp.desc())
		.all()
	)
	aes_key_string = db.query(Group).filter_by(id=group_name).first().shared_aes_key
	aes_key = str_to_bytes(aes_key_string)

	messages = [{
		"sender": get_email_by_user_id(db, msg.sender_id),
		"receiver": msg.group_name,
		"message": descifrar_mensaje_grupal(msg.message, aes_key),
		"signature": None,
		"hash": msg.hash,
		"timestamp": msg.timestamp,
	} for msg in data]
	return messages

def get_user_groups(db: Session, user_id: int):
	return (
		db.query(Group)
		.join(GroupUser)
		.filter(GroupUser.user_id == user_id)
		.all()
	)

def create_group(db: Session, name: str, user_id) -> Group:
	aes_key = bytes_to_str(get_random_bytes(32))
	new_group = Group(id=name, owner_id=user_id, shared_aes_key=aes_key)
	db.add(new_group)
	db.commit()
	db.refresh(new_group)
	return new_group

def get_group_owner_email(db: Session, group_name: str) -> str | None:
	group = db.query(Group).filter(Group.id == group_name).first()
	if group and group.owner:
		return group.owner.email
	return None

def get_group_non_participants(db: Session, group_name:str):
	group = db.query(Group).filter(Group.id == group_name).first()

	member_user_ids = db.query(GroupUser.user_id).filter(GroupUser.group_name == group_name).subquery()

	users = db.query(User).filter(
		User.id != group.owner_id,
		~User.id.in_(member_user_ids)
	).all()

	return [{"email": user.email} for user in users]