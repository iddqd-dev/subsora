from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import UserRead

class ReferralBase(BaseModel):
    referrer_id: int
    referred_id: int

class ReferralCreate(ReferralBase):
    pass

class ReferralUpdate(BaseModel):
    # Обычно рефералы не обновляются, но можно добавить поля при необходимости
    pass

class ReferralRead(ReferralBase):
    id: int
    created_at: datetime
    referrer: Optional[UserRead] = None
    referred: Optional[UserRead] = None

    class Config:
        from_attributes = True

class ReferralTierResponse(BaseModel):
    referrals: int
    discount: int