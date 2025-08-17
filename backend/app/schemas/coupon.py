from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CouponBase(BaseModel):
    code: str
    discount_percent: float
    max_uses: int = 1
    is_active: bool = True
    expires_at: Optional[datetime] = None

class CouponCreate(CouponBase):
    pass

class CouponUpdate(BaseModel):
    discount_percent: Optional[float] = None
    max_uses: Optional[int] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class CouponRead(CouponBase):
    id: int
    uses: int

    class Config:
        from_attributes = True