from sqlalchemy import Column, String, Float, DateTime
from backend.app.db.base_class import Base
from datetime import datetime, UTC

class Currency(Base):
    __tablename__ = "currencies"

    code = Column(String, primary_key=True)
    rate_to_usd = Column(Float, nullable=False)  # например: EUR = 1.12
    updated_at =  Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))