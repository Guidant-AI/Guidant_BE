import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

# Secret key retrieval
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secure_key")

# Function to create a JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": now,
        "sub": str(data.get("email"))
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# Function to decode a JWT
def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="The token has expired, please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="The token is invalid, authentication failed.")
