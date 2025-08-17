from typing import List

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.crud.base import CRUDBase
from backend.app.models.referral import Referral
from backend.app.schemas.referral import ReferralCreate, ReferralUpdate

class CRUDReferral(CRUDBase[Referral, ReferralCreate, ReferralUpdate]):
    @property
    def _eager_loading_options(self):
        # Для рефералов грузим того, кто пригласил, и того, кого пригласили
        return [
            selectinload(self.model.referrer),
            selectinload(self.model.referred)
        ]

    async def get_user_referrals(
        self, db: AsyncSession, *, referrer_id: int
    ) -> List[Referral]:
        """Получить всех пользователей, которых пригласил данный пользователь"""
        result = await db.execute(
            select(self.model)
            .filter(Referral.referrer_id == referrer_id) # type: ignore
            .options(*self._eager_loading_options)
        )
        return list(result.scalars().all())

    async def get_referrer(
        self, db: AsyncSession, *, referred_id: int
    ) -> Referral | None:
        """Получить того, кто пригласил данного пользователя"""
        result = await db.execute(
            select(self.model).filter(Referral.referred_id == referred_id) # type: ignore
        )
        return result.scalars().first()

    async def count_user_referrals(
            self, db: AsyncSession, *, referrer_id: int
    ) -> int:
        """Подсчитывает количество рефералов пользователя эффективно."""
        query = select(func.count()).select_from(self.model).filter(self.model.referrer_id == referrer_id) # type: ignore
        result = await db.execute(query)
        # .scalar_one() вернет одно значение (число) из результата
        return result.scalar_one()


referral = CRUDReferral(Referral)