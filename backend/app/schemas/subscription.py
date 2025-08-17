from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from .user import UserRead
from .plan import PlanRead

class SubscriptionBase(BaseModel):
    user_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionCreateRequest(BaseModel):
    """Схема, которую клиент отправляет для создания подписки."""
    plan_id: int
    coupon_code: Optional[str] = None
    currency: Optional[str] = "USD"

class SubscriptionUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SubscriptionRead(SubscriptionBase):
    id: int
    start_date: datetime
    user: UserRead
    plan: PlanRead

    class Config:
        from_attributes = True