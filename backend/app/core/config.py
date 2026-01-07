import os
from pydantic_settings import BaseSettings
from typing import Optional, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE_PATH = "/app/backend/.env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Subsora"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    REFERRAL_TIERS: List[Tuple[int, int]] = [
        (50, 15),
        (30, 10),
        (15, 5),
        (5, 3),
    ]
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@domain:5432/subsora"

    # Security
    JWT_SECRET_KEY: str = "supersecret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None

    # Payment settings
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Redis for caching
    REDIS_URL: Optional[str] = None

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    VPN_PANEL_URL: str = "https://domain.com"
    VPN_PANEL_PORT: int = 8002
    VPN_PANEL_USER: str = "admin"
    VPN_PANEL_PASSWORD: str = "password"
    VPN_PANEL_SSL: bool = True

    # Telegram bot - обязательные поля
    TELEGRAM_BOT_TOKEN: str = "123"
    TELEGRAM_BOT_SECRET: str = "123"

    class Config:
        # Используем .env файл
        env_file = ENV_FILE_PATH
        print(env_file)
        case_sensitive = True
        # Приоритет переменным окружения над .env файлом
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = Settings()
