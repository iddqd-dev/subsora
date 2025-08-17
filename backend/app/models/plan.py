from sqlalchemy import Column, Integer, String, Float, Boolean
from backend.app.db.base_class import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)  # в долларах/евро/любая валюта
    duration_days = Column(Integer, nullable=False)  # сколько дней длится подписка
    is_active = Column(Boolean, default=True)