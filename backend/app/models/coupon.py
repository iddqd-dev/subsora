from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from backend.app.db.base_class import Base
from datetime import datetime

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    discount_percent = Column(Float, nullable=False)
    max_uses = Column(Integer, default=1)
    uses = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)