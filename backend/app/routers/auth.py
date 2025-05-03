from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserOut, Token, UserLogin
from app.models import User
from app.db import SessionLocal
from app.auth.utils import get_password_hash, verify_password
from app.auth.jwt import create_access_token
from app.auth.totp import generate_totp_secret, verify_totp_token

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=UserOut)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(email=user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    secret = generate_totp_secret()
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        totp_secret=secret,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/signin", response_model=Token)
def signin(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_totp_token(user.totp_secret, login_data.totp_code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
