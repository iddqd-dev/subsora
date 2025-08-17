from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime, UTC

from sqlalchemy.orm import selectinload

from backend.app.crud.base import CRUDBase
from backend.app.models.subscription import Subscription
from backend.app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

class CRUDSubscription(CRUDBase[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    @property
    def _eager_loading_options(self):
        # Говорим, что для подписок всегда нужно подгружать пользователя и план
        return [
            selectinload(self.model.user),
            selectinload(self.model.plan)
        ]
    async def get_user_subscriptions(
        self, db: AsyncSession, *, user_id: int
    ) -> List[Subscription]:
        result = await db.execute(
            select(self.model)
            .filter(Subscription.user_id == user_id) # type: ignore
            .options(*self._eager_loading_options)
        )
        return list(result.scalars().all())

    def _get_active_subscription_query(self, user_id: int):
        """Базовый запрос, который могут использовать другие методы."""
        now = datetime.now(UTC)
        return select(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.end_date > now
            )
        )

    async def get_active_subscription(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[Subscription]:
        """
        Получает активную подписку БЕЗ связей.
        Быстро, для внутреннего использования.
        """
        query = self._get_active_subscription_query(user_id)
        result = await db.execute(query.order_by(self.model.end_date.desc()))
        return result.scalars().first()

    async def get_active_subscription_with_details(
            self, db: AsyncSession, *, user_id: int
    ) -> Optional[Subscription]:
        """
        Получает активную подписку С ПОЛНЫМИ ДАННЫМИ.
        Для использования в API.
        """
        query = self._get_active_subscription_query(user_id)
        query = query.order_by(self.model.end_date.desc()).options(*self._eager_loading_options)
        result = await db.execute(query)
        return result.scalars().first()

subscription = CRUDSubscription(Subscription)