import os
from typing import List, Optional, Tuple

from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def resolve_env_file_path() -> str:
    explicit_env_file = os.getenv("SETTINGS_ENV_FILE")
    if explicit_env_file:
        return explicit_env_file

    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production":
        return os.path.join(BASE_DIR, ".env")

    dev_path = os.path.join(BASE_DIR, ".env.dev")
    if os.path.exists(dev_path):
        return dev_path

    return os.path.join(BASE_DIR, ".env")


ENV_FILE_PATH = resolve_env_file_path()


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
    DATABASE_URL: Optional[str] = None

    # Security
    JWT_SECRET_KEY: Optional[str] = None
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
    DEBUG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    VPN_PANEL_URL: str = "https://domain.com"
    VPN_PANEL_PORT: int = 8002
    VPN_PANEL_USER: Optional[str] = None
    VPN_PANEL_PASSWORD: Optional[str] = None
    VPN_PANEL_SSL: bool = True

    # Telegram bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_BOT_SECRET: Optional[str] = None

    # Native Xray settings
    XRAY_CONFIG_PATH: Optional[str] = None
    XRAY_PROCESS_NAME: Optional[str] = None

    # Reality keys
    XRAY_PRIVATE_KEY: Optional[str] = None
    XRAY_PUBLIC_KEY: Optional[str] = None
    XRAY_SHORT_ID: Optional[str] = None

    class Config:
        env_file = ENV_FILE_PATH
        case_sensitive = True
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
