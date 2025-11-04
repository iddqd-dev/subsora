"""API клиент для взаимодействия с Subsora backend."""
import aiohttp
import logging
from typing import Dict, Any
import json

from .config import settings

logger = logging.getLogger(__name__)


class SubsoraApiClientError(Exception):
    """Базовое исключение API клиента."""
    pass


class UserNotFoundError(SubsoraApiClientError):
    """Пользователь не найден."""
    pass


class SubsoraApiClient:
    """Клиент для работы с Subsora API."""

    def __init__(self, base_url: str, bot_secret: str):
        self._base_url = base_url.rstrip('/')
        self._headers = {
            "X-Bot-Token": bot_secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._session: aiohttp.ClientSession | None = None
        logger.info(f"API Client initialized with base URL: {self._base_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Создает и возвращает сессию."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=10.0)
            )
        return self._session

    async def get_profile(self, telegram_id: int) -> Dict[str, Any]:
        """
        Получает полный профиль пользователя.

        Args:
            telegram_id: Telegram ID пользователя

        Returns:
            Dict с данными профиля

        Raises:
            UserNotFoundError: Если пользователь не найден
            SubsoraApiClientError: При других ошибках API
        """
        session = await self._get_session()
        url = f"{self._base_url}/bot/profile/{telegram_id}"

        try:
            async with session.get(url, headers=self._headers) as response:
                if response.status == 404:
                    raise UserNotFoundError(f"User with telegram_id {telegram_id} not found")

                response.raise_for_status()

                try:
                    data = await response.json()
                    logger.info(f"Profile retrieved for user {telegram_id}")
                    return data
                except json.JSONDecodeError:
                    text = await response.text()
                    raise SubsoraApiClientError(f"Invalid JSON response: {text}")

        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error getting profile: {e.status} - {e.message}")
            raise SubsoraApiClientError(f"API request failed: {e.status}") from e
        except aiohttp.ClientError as e:
            logger.error(f"Network error getting profile: {e}")
            raise SubsoraApiClientError(f"Network error: {e}") from e

    async def register_trial(
            self,
            telegram_id: int,
            full_name: str,
            username: str | None
    ) -> Dict[str, Any]:
        """
        Регистрирует нового пользователя с триалом.

        Args:
            telegram_id: Telegram ID
            full_name: Полное имя пользователя
            username: Username в Telegram (опционально)

        Returns:
            Dict с данными регистрации

        Raises:
            SubsoraApiClientError: При ошибках регистрации
        """
        session = await self._get_session()
        url = f"{self._base_url}/bot/register-trial"

        payload = {
            "telegram_id": telegram_id,
            "full_name": full_name,
            "username": username
        }

        try:
            async with session.post(url, json=payload, headers=self._headers) as response:
                if response.status == 409:
                    raise SubsoraApiClientError("User already exists")

                response.raise_for_status()
                data = await response.json()
                logger.info(f"Trial registered for user {telegram_id}")
                return data

        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error registering trial: {e.status} - {e.message}")
            raise SubsoraApiClientError(f"Registration failed: {e.status}") from e
        except aiohttp.ClientError as e:
            logger.error(f"Network error registering trial: {e}")
            raise SubsoraApiClientError(f"Network error: {e}") from e

    async def get_available_plans(self) -> list[Dict[str, Any]]:
        """
        Получает список доступных тарифных планов.

        Returns:
            Список тарифов
        """
        session = await self._get_session()
        url = f"{self._base_url}/bot/plans"

        try:
            async with session.get(url, headers=self._headers) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info("Plans list retrieved")
                return data.get('plans', [])

        except aiohttp.ClientError as e:
            logger.error(f"Error getting plans: {e}")
            raise SubsoraApiClientError(f"Failed to get plans: {e}") from e

    async def close(self):
        """Закрывает сессию клиента."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("API Client session closed")


# Создаем singleton экземпляр
api_client = SubsoraApiClient(
    base_url=settings.subsora_api_url,
    bot_secret=settings.subsora_api_bot_secret
)