from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Настройки бота из переменных окружения."""
    bot_token: str
    subsora_api_url: str
    subsora_api_bot_secret: str

    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = 'utf-8'


settings = Settings()