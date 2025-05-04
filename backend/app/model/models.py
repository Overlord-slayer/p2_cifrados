from sqlalchemy import Column, Integer, String, Boolean, LargeBinary
from app.db.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    totp_secret = Column(String, nullable=True)
    public_key = Column(LargeBinary, nullable=True)   # ECC/RSA pública para cifrado o firma
    is_active = Column(Boolean, default=True)
