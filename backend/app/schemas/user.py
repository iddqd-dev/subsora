from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    referral_code: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserCreateFromTelegram(BaseModel):
    telegram_id: int
    full_name: str
    username: Optional[str] = None

class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    referral_code: Optional[str] = None
    telegram_id: Optional[int] = None
    subscription_url: Optional[str] = None

    class Config:
        from_attributes = True