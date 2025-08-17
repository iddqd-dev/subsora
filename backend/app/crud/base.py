from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query, InstrumentedAttribute, selectinload  # Импортируем selectinload

from backend.app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    @property
    def _eager_loading_options(self) -> List[InstrumentedAttribute]:
        """
        Возвращает список связей для жадной загрузки.
        Переопределяется в дочерних классах.
        Пример: [selectinload(self.model.user), selectinload(self.model.plan)]
        """
        return []

    async def get(self, db: AsyncSession, _id: Any) -> Optional[ModelType]:
        query = select(self.model).filter(self.model.id == _id)  # type: ignore
        if self._eager_loading_options:
            query = query.options(*self._eager_loading_options)

        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
            self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        query = select(self.model)
        if self._eager_loading_options:
            query = query.options(*self._eager_loading_options)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        # После коммита сессия инвалидирует объект, нужно его "освежить"
        await db.refresh(db_obj)

        # После refresh связи не загружены. Мы должны получить объект заново
        # с жадной загрузкой, чтобы вернуть его в API.
        if self._eager_loading_options:
            return await self.get(db, _id=db_obj.id)

        return db_obj

    async def update(
            self,
            db: AsyncSession,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        if self._eager_loading_options:
            return await self.get(db, _id=db_obj.id)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.id == id)) # type: ignore
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj