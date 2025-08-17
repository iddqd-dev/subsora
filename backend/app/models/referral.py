from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.db.base_class import Base
from datetime import datetime, UTC


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # кто пригласил
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # кто зарегистрировался
    created_at =  Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_sent")
    referred = relationship("User", foreign_keys=[referred_id], back_populates="referrals_received")