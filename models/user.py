from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    email: EmailStr
    password: str
    created_on: Optional[datetime] = datetime.utcnow()

