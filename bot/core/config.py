from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки бота из переменных окружения или .env файла."""
    bot_token: str
    subsora_api_url: str
    subsora_api_bot_secret: str

    model_config = SettingsConfigDict(
        env_file='/app/.env',  # Путь в контейнере
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings()