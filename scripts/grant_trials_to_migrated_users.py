import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, Column, Integer, String, DateTime, BigInteger, Boolean, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Настройки ---
# Убедись, что строка подключения к базе subsora верна
SUBSORA_DB_URL = "postgresql+asyncpg://zerity_cicd:pgpwd4dronesecurely@91.108.243.42:5432/subsora"

# --- Определяем SQLAlchemy модели (только те, что нужны) ---
BaseSubsora = declarative_base()


class SubsoraUser(BaseSubsora):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String)


class SubsoraPlan(BaseSubsora):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class SubsoraSubscription(BaseSubsora):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    start_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_date = Column(DateTime(timezone=True), nullable=False)


async def grant_trials():
    print("--- Starting Grant Trial Subscriptions Script ---")

    subsora_engine = create_async_engine(SUBSORA_DB_URL)
    AsyncSubsoraSession = sessionmaker(subsora_engine, class_=AsyncSession)

    async with AsyncSubsoraSession() as session:
        # 1. Находим ID триального плана в базе subsora
        # Используем ilike для регистронезависимого поиска
        plan_result = await session.execute(
            select(SubsoraPlan).where(SubsoraPlan.name.ilike('%пробный%'))
        )
        trial_plan = plan_result.scalars().first()

        if not trial_plan:
            print("ERROR: Trial plan ('...пробный...') not found in subsora database. Aborting.")
            return

        print(f"Found trial plan: '{trial_plan.name}' (ID: {trial_plan.id})")

        # 2. Находим всех пользователей, у которых ЕЩЕ НЕТ активной подписки
        # (Это более сложный запрос, но самый правильный способ)
        now = datetime.now(timezone.utc)

        # Подзапрос, который находит всех user_id с активной подпиской
        subquery = select(SubsoraSubscription.user_id).where(SubsoraSubscription.end_date > now)

        # Основной запрос: выбрать всех пользователей, чей ID НЕ находится в списке из подзапроса
        users_without_subs_stmt = select(SubsoraUser).where(SubsoraUser.id.notin_(subquery))

        users_result = await session.execute(users_without_subs_stmt)
        users_to_grant_trial = users_result.scalars().all()

        if not users_to_grant_trial:
            print("No users found without an active subscription. Nothing to do.")
            await subsora_engine.dispose()
            return

        print(f"Found {len(users_to_grant_trial)} users who need a trial subscription.")

        granted_count = 0
        for user in users_to_grant_trial:
            # 3. Создаем новую триальную подписку
            new_trial_sub = SubsoraSubscription(
                user_id=user.id,
                plan_id=trial_plan.id,
                start_date=now,
                end_date=now + timedelta(days=30)
            )
            session.add(new_trial_sub)
            granted_count += 1
            print(f"  (+) Prepared 30-day trial for user {user.email} (ID: {user.id})")

        if granted_count > 0:
            print(f"\nCommitting {granted_count} new trial subscriptions...")
            await session.commit()
            print("✅ Trials granted successfully.")
        else:
            print("No new subscriptions were prepared.")

    await subsora_engine.dispose()
    print("\n--- Trial Granting Finished ---")


if __name__ == "__main__":
    asyncio.run(grant_trials())