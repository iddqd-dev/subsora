import uuid

from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from datetime import datetime, timezone

from sqlalchemy.orm import relationship

from backend.app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)  # Добавить
    is_superuser = Column(Boolean, default=False)  # Добавить
    created_at =  Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # Добавить
    referral_code = Column(String, unique=True, nullable=True)  # Добавить для реферальной системы
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    subscription_url = Column(String, nullable=True)


    subscriptions = relationship("Subscription", back_populates="user")
    referrals_sent = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")
    referrals_received = relationship("Referral", foreign_keys="Referral.referred_id", back_populates="referred")

    def generate_referral_code(self):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()