from datetime import datetime, timedelta
import jwt
from fastapi import Response
from dotenv import load_dotenv
import os
from passlib.hash import sha256_crypt
load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("JWT_ALGORITHM")
EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRATION_MINUTES"))


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() +  timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        print("JWT Decode error:", str(e))
        return None



def set_access_token_cookie(response: Response, user_id: str):
    token = create_access_token({"sub": str(user_id)})
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=3600,            # 1 hour
        expires=3600,
        secure=False,            # Set to True in production with HTTPS
        samesite="lax"
    )



def hash_password(password: str) -> str:
    return sha256_crypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return sha256_crypt.verify(plain_password, hashed_password)
