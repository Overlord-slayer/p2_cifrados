from fastapi import APIRouter, Request, HTTPException
from app.auth.google.oauth2 import oauth  # renómbralo a oauth_config.py
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["google"])

@router.get("/google/login")
async def google_login(request: Request):
	try:
		redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
		return await oauth.google.authorize_redirect(request, redirect_uri)
	except Exception as e:
		raise HTTPException(status_code=500, detail="Internal server error")
