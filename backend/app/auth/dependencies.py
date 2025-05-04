from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token, expected_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]
