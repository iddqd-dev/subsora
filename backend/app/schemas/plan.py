from pydantic import BaseModel
from typing import Optional

class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration_days: int
    is_active: bool = True

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None
    is_active: Optional[bool] = None

class PlanRead(PlanBase):
    id: int

    class Config:
        from_attributes = True