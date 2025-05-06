import base64
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import pyotp
import qrcode
from app.auth.google.oauth2 import oauth  # renómbralo a oauth_config.py
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.model.models import User

load_dotenv()

router = APIRouter(prefix="/auth", tags=["google"])

@router.get("/google/login")
async def google_login(request: Request):
	redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
	return await oauth.google.authorize_redirect(request, redirect_uri)