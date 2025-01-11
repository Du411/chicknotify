from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserData(BaseModel):
    username: str
    email: EmailStr
    password: str
    telegram_id: Optional[str] = None
    discord_id: Optional[str] = None
    notification_type_id: int

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    username: str
    email: str
    telegram_id: Optional[str] = None
    discord_id: Optional[str] = None
    notification_type_id: int
    created_at: datetime

    class Config:
        from_attributes = True
