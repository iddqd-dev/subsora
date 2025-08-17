import asyncio
import uuid
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime
from passlib.context import CryptContext
from sqlalchemy.sql.sqltypes import Boolean

# --- Настройки ---
WHIMVPN_DB_URL = "postgresql+asyncpg://zerity_cicd:pgpwd4dronesecurely@91.108.243.42:5432/whimvpn"
SUBSORA_DB_URL = "postgresql+asyncpg://zerity_cicd:pgpwd4dronesecurely@91.108.243.42:5432/subsora"

# --- Вспомогательные утилиты ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# --- Модели для старой базы (whimvpn) ---
BaseWhim = declarative_base()


class WhimReferral(BaseWhim):
    __tablename__ = 'referrals'
    referral_id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    referred_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)


class WhimUser(BaseWhim):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String)
    fullname = Column(String)
    subscription_url = Column(String)
    # ... другие поля не участвуют в миграции, можно не объявлять


# --- Модели для новой базы (subsora) ---
BaseSubsora = declarative_base()


class SubsoraReferral(BaseSubsora):
    __tablename__ = 'referrals'
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    referred_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default='now()')


class SubsoraUser(BaseSubsora):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    subscription_url = Column(String, nullable=True)
    referral_code = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, server_default='now()')
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


# --- Основная логика миграции ---
async def migrate_data():
    print("--- Starting Full Migration (Users & Referrals) ---")

    whim_engine = create_async_engine(WHIMVPN_DB_URL)
    subsora_engine = create_async_engine(SUBSORA_DB_URL)

    AsyncWhimSession = sessionmaker(whim_engine, class_=AsyncSession)
    AsyncSubsoraSession = sessionmaker(subsora_engine, class_=AsyncSession)

    # Словарь для сопоставления старых ID с новыми
    # { old_whim_user_id: new_subsora_user_id }
    user_id_map = {}

    async with AsyncWhimSession() as whim_session, AsyncSubsoraSession() as subsora_session:
        # === ЭТАП 1: Миграция Пользователей ===
        print("\n[PHASE 1] Migrating users...")

        old_users_result = await whim_session.execute(select(WhimUser))
        old_users = old_users_result.scalars().all()
        print(f"Found {len(old_users)} users in whimvpn.")

        new_users_to_commit = []
        for old_user in old_users:
            if not old_user.telegram_id:
                continue

            existing_user_result = await subsora_session.execute(
                select(SubsoraUser).where(SubsoraUser.telegram_id == old_user.telegram_id)
            )
            existing_user = existing_user_result.scalars().first()

            if existing_user:
                # Если пользователь уже есть, просто запоминаем сопоставление ID
                user_id_map[old_user.user_id] = existing_user.id
                continue

            temp_email = f"{old_user.telegram_id}@telegram.user"
            random_password = str(uuid.uuid4())
            referral_code = str(uuid.uuid4())[:8].upper()

            new_user = SubsoraUser(
                telegram_id=old_user.telegram_id,
                full_name=old_user.fullname,
                email=temp_email,
                hashed_password=hash_password(random_password),
                subscription_url=old_user.subscription_url,
                referral_code=referral_code
                # Поля is_active и is_superuser будут заполнены
                # значениями по умолчанию из модели
            )
            new_users_to_commit.append((old_user.user_id, new_user))

        if new_users_to_commit:
            print(f"Preparing {len(new_users_to_commit)} new users...")
            subsora_session.add_all([user for _, user in new_users_to_commit])
            await subsora_session.flush()  # Отправляем в БД, чтобы получить новые ID

            # Заполняем карту ID после того, как SQLAlchemy присвоила ID
            for old_id, new_user_obj in new_users_to_commit:
                user_id_map[old_id] = new_user_obj.id

            await subsora_session.commit()
            print("Users committed successfully.")
        else:
            print("No new users to migrate.")

        # === ЭТАП 2: Миграция Рефералов ===
        print("\n[PHASE 2] Migrating referrals...")

        old_referrals_result = await whim_session.execute(select(WhimReferral))
        old_referrals = old_referrals_result.scalars().all()
        print(f"Found {len(old_referrals)} referral records in whimvpn.")

        migrated_ref_count = 0
        for old_ref in old_referrals:
            # Находим новые ID для реферера и реферала
            new_referrer_id = user_id_map.get(old_ref.referrer_id)
            new_referred_id = user_id_map.get(old_ref.referred_id)

            if not new_referrer_id or not new_referred_id:
                print(f"Skipping referral: cannot map old IDs ({old_ref.referrer_id} -> {old_ref.referred_id})")
                continue

            # Проверяем, не существует ли уже такая связь
            existing_ref_result = await subsora_session.execute(
                select(SubsoraReferral).where(
                    SubsoraReferral.referrer_id == new_referrer_id,
                    SubsoraReferral.referred_id == new_referred_id
                )
            )
            if existing_ref_result.scalars().first():
                continue

            # Создаем новую реферальную запись
            new_referral = SubsoraReferral(
                referrer_id=new_referrer_id,
                referred_id=new_referred_id
            )
            subsora_session.add(new_referral)
            migrated_ref_count += 1

        if migrated_ref_count > 0:
            print(f"Committing {migrated_ref_count} new referral records...")
            await subsora_session.commit()
            print("Referrals committed successfully.")
        else:
            print("No new referrals to migrate.")

    await whim_engine.dispose()
    await subsora_engine.dispose()

    print("\n--- Full Migration Finished ---")


if __name__ == "__main__":
    asyncio.run(migrate_data())