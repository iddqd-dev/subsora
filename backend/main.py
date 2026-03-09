from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from backend.app.api.router import api_router
from backend.app.core.config import settings
from backend.app.core.exceptions import database_exception_handler, validation_exception_handler
from backend.app.core.middleware import LoggingMiddleware
import logging

from backend.app.db.session import async_session
from backend.app.services.vpn_manager import VpnManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Subsora API",
    version="0.1.0",
    description="Subscription management API"
)

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware) # type: ignore

app.add_exception_handler(IntegrityError, database_exception_handler) # type: ignore
app.add_exception_handler(ValueError, validation_exception_handler) # type: ignore

app.include_router(api_router)


@app.on_event("startup")
async def sync_xray_on_startup() -> None:
    """
    При старте backend синхронизируем Xray с актуальными подписками из БД.
    """
    try:
        async with async_session() as db:
            async with VpnManager() as vpn:
                await vpn.sync_active_users(db)
    except Exception as exc:
        # Do not fail API startup if Xray sync is temporarily unavailable.
        logging.getLogger(__name__).exception("Xray startup sync failed: %s", exc)

