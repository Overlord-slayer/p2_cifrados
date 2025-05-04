from fastapi import APIRouter, Request
from app.auth.google.oauth2 import oauth  # renómbralo a oauth_config.py
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["google"])

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)
