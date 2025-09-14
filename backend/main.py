from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from backend.app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import database_exception_handler, validation_exception_handler
from app.core.middleware import LoggingMiddleware
import logging

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

