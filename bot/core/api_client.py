import aiohttp
from pydantic_settings import BaseSettings
from typing import Dict, Any
from pathlib import Path
import json


# 1. Класс Settings остается без изменений
class Settings(BaseSettings):
    bot_token: str = ''
    subsora_api_url: str = ''
    subsora_api_bot_secret: str = ''

    class Config:
        env_file = Path(__file__).parent.parent / ".env"


settings = Settings()


# 2. Кастомные исключения остаются без изменений
class SubsoraApiClientError(Exception):
    pass


class UserNotFoundError(SubsoraApiClientError):
    pass


# 3. Сам API-клиент, переписанный на aiohttp
class SubsoraApiClient:
    def __init__(self, base_url: str, bot_secret: str):
        print(base_url)
        self._base_url = base_url
        self._headers = {
            "X-Bot-Token": bot_secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # aiohttp требует, чтобы ClientSession создавался внутри async-функции
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Создает и возвращает сессию, если она еще не создана."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                base_url=self._base_url,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=10.0)
            )
        return self._session

    async def get_profile(self, telegram_id: int) -> Dict[str, Any]:
        """
        Получает полный профиль пользователя от бэкенда Subsora.
        """
        session = await self._get_session()
        try:
            async with session.get(f"bot/profile/{telegram_id}",
                                   headers=self._headers) as response:
                if response.status == 404:
                    raise UserNotFoundError(f"User with telegram_id {telegram_id} not found.")

                # Пробрасываем другие HTTP-ошибки
                response.raise_for_status()

                try:
                    return await response.json()
                except json.JSONDecodeError:
                    # Если ответ не JSON, но статус 200 OK
                    raise SubsoraApiClientError(f"API returned non-JSON response: {await response.text()}")

        except aiohttp.ClientResponseError as e:
            # Обрабатываем ошибки HTTP (500, 403 и т.д.)
            raise SubsoraApiClientError(f"API request failed: {e.status} - {e.message}") from e
        except aiohttp.ClientError as e:
            # Обрабатываем ошибки сети (недоступен хост, таймаут)
            raise SubsoraApiClientError(f"Network error while requesting profile: {e}") from e

    async def register_trial(self, telegram_id: int, full_name: str, username: str | None) -> Dict[str, Any]:
        """Регистрирует нового пользователя и выдает ему триал."""
        payload = {
            "telegram_id": telegram_id,
            "full_name": full_name,
            "username": username
        }
        try:
            # Используем POST вместо GET
            async with self._session.post("bot/register-trial", json=payload, headers=self._headers) as response:
                if response.status == 409:  # Conflict
                    raise SubsoraApiClientError("User already exists.")

                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            raise SubsoraApiClientError(f"API request failed: {e.status} - {e.message}") from e
        except aiohttp.ClientError as e:
            raise SubsoraApiClientError(f"Network error during registration: {e}") from e

    async def close(self):
        """Закрывает сессию клиента. Важно вызывать при остановке бота."""
        if self._session and not self._session.closed:
            await self._session.close()


# 4. Создаем единый экземпляр клиента (без изменений)
api_client = SubsoraApiClient(
    base_url=settings.subsora_api_url,
    bot_secret=settings.subsora_api_bot_secret
)


