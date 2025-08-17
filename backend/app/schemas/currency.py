from pydantic import BaseModel
from datetime import datetime

class CurrencyBase(BaseModel):
    code: str
    rate_to_usd: float

class CurrencyCreate(CurrencyBase):
    pass

class CurrencyUpdate(BaseModel):
    rate_to_usd: float

class CurrencyRead(CurrencyBase):
    updated_at: datetime

    class Config:
        from_attributes = True