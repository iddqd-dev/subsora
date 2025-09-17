import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.crud.base import CRUDBase
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate, UserCreateFromTelegram  # Добавим UserUpdate
from backend.app.core.security import hash_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_user_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        result = await db.execute(select(self.model).filter(User.email == email)) # type: ignore
        return result.scalars().first()

    async def get_by_telegram_id(self, db: AsyncSession, *, telegram_id: int) -> User | None:
        result = await db.execute(select(self.model).filter(self.model.telegram_id == telegram_id)) # type: ignore
        return result.scalars().first()

    async def create_from_telegram(self, db: AsyncSession, *, obj_in: UserCreateFromTelegram) -> User:
        """Создает пользователя на основе данных из Telegram."""
        # Генерируем временные данные для обязательных полей
        temp_email = f"{obj_in.telegram_id}@telegram.user"
        random_password = '123456'

        # Проверяем, не занят ли уже такой временный email
        existing_user = await self.get_user_by_email(db, email=temp_email)
        if existing_user:
            # Если так случилось, что telegram_id уже есть, но под другим email (маловероятно)
            # или email занят, добавляем случайный суффикс
            temp_email = f"{obj_in.telegram_id}_{str(uuid.uuid4())[:4]}@telegram.user"

        db_obj = User(
            email=temp_email,
            hashed_password=hash_password(random_password),
            full_name=obj_in.full_name,
            telegram_id=obj_in.telegram_id,
        )
        db_obj.generate_referral_code()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=hash_password(obj_in.password),
        )
        db_obj.generate_referral_code()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

user = CRUDUser(User)