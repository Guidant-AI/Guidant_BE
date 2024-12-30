from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    created_on: Optional[datetime] = datetime.utcnow()

class LoginRequest(BaseModel):
    email: str
    password: str
    otp: str

class LogoutRequest(BaseModel):
    token: str

class SendOtpRequest(BaseModel):
    email: str
    password: str
class Profile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    class_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    isComplete: Optional[bool] = False
