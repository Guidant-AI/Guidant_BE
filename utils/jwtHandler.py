import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = "0e9df952cc068a7f870261bf12c914addfba01adb4a2b97d352ec71fac825f5d05cbfd6f689678839a244b16b823649e93bee0ee48aebcbc930039703eebba14"  # Replace with a secure secret key

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
