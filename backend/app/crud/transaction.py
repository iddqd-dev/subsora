from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.crud.base import CRUDBase
from backend.app.models.subscription import Subscription
from backend.app.models.transaction import Transaction
from backend.app.schemas.transaction import TransactionCreate, TransactionUpdate


class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    @property
    def _eager_loading_options(self):
        """Определяет связи для жадной загрузки для всех методов."""
        return [
            selectinload(self.model.user),
            selectinload(self.model.subscription).selectinload(Subscription.plan)
        ]

    # --- Обновляем кастомные методы ---

    async def get_user_transactions(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """
        Получает транзакции пользователя с деталями (user, subscription, plan).
        Готов для использования в API.
        """
        query = (
            select(self.model)
            .filter(self.model.user_id == user_id) # type: ignore
            .order_by(self.model.created_at.desc())
            .options(*self._eager_loading_options)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_status(
        self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """
        Получает транзакции по статусу с деталями.
        Готов для использования в API.
        """
        query = (
            select(self.model)
            .filter(self.model.status == status) # type: ignore
            .options(*self._eager_loading_options)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

transaction = CRUDTransaction(Transaction)