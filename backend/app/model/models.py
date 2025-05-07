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

class Message(Base):
	__tablename__ = "messages"

	id = Column(Integer, primary_key=True, index=True)
	
	sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	
	message = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	# Relationships to link to User
	sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
	receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")