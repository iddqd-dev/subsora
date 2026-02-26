from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime, timezone

from backend.app.crud.base import CRUDBase
from backend.app.models.coupon import Coupon
from backend.app.schemas.coupon import CouponCreate, CouponUpdate

class CRUDCoupon(CRUDBase[Coupon, CouponCreate, CouponUpdate]):
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Coupon]:
        result = await db.execute(select(self.model).filter(Coupon.code == code)) # type: ignore
        return result.scalars().first()

    async def validate_coupon(self, db: AsyncSession, *, code: str) -> Optional[Coupon]:
        """Проверяет валидность купона"""
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(self.model).filter(
                and_(
                    Coupon.code == code,
                    Coupon.is_active == True,
                    Coupon.uses < Coupon.max_uses,
                    # Если expires_at NULL, то купон не истекает
                    (Coupon.expires_at.is_(None)) | (Coupon.expires_at > now)
                )
            )
        )
        return result.scalars().first()

    async def use_coupon(self, db: AsyncSession, *, coupon: Coupon) -> Coupon:
        """Увеличивает счетчик использования купона"""
        coupon.uses += 1
        db.add(coupon)
        await db.commit()
        await db.refresh(coupon)
        return coupon

coupon = CRUDCoupon(Coupon)