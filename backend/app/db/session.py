from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from backend.app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args={
        "server_settings": {"application_name": settings.PROJECT_NAME},
    },
    pool_pre_ping=True,
    pool_recycle=3600
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session