from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.model.models import User
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.google.oauth2 import oauth
from fastapi.responses import RedirectResponse

import pyotp

router = APIRouter()

@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    
    #  CORRECTO: solo pasa `token=`
    user_info = await oauth.google.userinfo(token=token)

    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google response")

    user = db.query(User).filter_by(email=email).first()

    if not user:
        totp_secret = pyotp.random_base32()
        user = User(email=email, hashed_password="", totp_secret=totp_secret)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token({"sub": email})
    refresh_token = create_refresh_token({"sub": email})

    return RedirectResponse(
        url=f"http://localhost:3000/oauth-callback?access_token={access_token}&refresh_token={refresh_token}&totp_enabled={bool(user.totp_secret)}"
    )
