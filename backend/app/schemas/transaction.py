from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .user import UserRead
from .subscription import SubscriptionRead # Импортируем схему подписки

class TransactionBase(BaseModel):
    user_id: int
    amount: float
    currency: str = "USD"
    status: str = "pending"
    subscription_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[float] = None

class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    user: UserRead  # <-- Добавляем пользователя
    subscription: Optional[SubscriptionRead] = None # <-- Добавляем подписку

    class Config:
        from_attributes = True