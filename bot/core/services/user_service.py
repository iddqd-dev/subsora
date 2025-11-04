"""Сервис для работы с пользователями."""
import logging
from typing import Dict, Any

from ..api_client import SubsoraApiClient, UserNotFoundError
from ..texts import BotTexts

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для бизнес-логики работы с пользователями."""

    def __init__(self, api_client: SubsoraApiClient):
        self.api = api_client

    async def get_or_create_user(
            self,
            telegram_id: int,
            full_name: str,
            username: str | None
    ) -> Dict[str, Any]:
        """
        Получает пользователя или создаёт нового с триалом.

        Args:
            telegram_id: Telegram ID
            full_name: Полное имя
            username: Username (опционально)

        Returns:
            Dict с данными пользователя
        """
        try:
            return await self.api.get_profile(telegram_id)
        except UserNotFoundError:
            logger.info(f"User {telegram_id} not found, creating trial")
            return await self.api.register_trial(telegram_id, full_name, username)

    def format_profile_text(self, profile_data: Dict[str, Any]) -> str:
        """
        Форматирует данные профиля в текст для отображения.

        Args:
            profile_data: Данные профиля от API

        Returns:
            Отформатированный текст
        """
        user = profile_data.get('user', {})
        subscription = profile_data.get('active_subscription')

        # Базовая информация
        lines = [BotTexts.PROFILE_HEADER]

        full_name = user.get('full_name', 'Без имени')
        lines.append(BotTexts.PROFILE_NAME.format(full_name=full_name))

        if user.get('email'):
            lines.append(BotTexts.PROFILE_EMAIL.format(email=user['email']))

        if user.get('username'):
            lines.append(BotTexts.PROFILE_USERNAME.format(username=user['username']))

        # Информация о подписке
        if subscription:
            lines.append(BotTexts.ACTIVE_SUBSCRIPTION)

            plan = subscription.get('plan', {})
            plan_name = plan.get('name', 'N/A')
            lines.append(BotTexts.SUBSCRIPTION_PLAN.format(plan_name=plan_name))

            end_date = subscription.get('end_date', 'N/A')
            lines.append(BotTexts.SUBSCRIPTION_END.format(end_date=end_date))
        else:
            lines.append(BotTexts.NO_SUBSCRIPTION)

        return "\n".join(lines)

    def format_subscription_url(self, profile_data: Dict[str, Any]) -> str:
        """
        Форматирует сообщение со ссылкой подключения.

        Args:
            profile_data: Данные профиля от API

        Returns:
            Отформатированный текст со ссылкой
        """
        user = profile_data.get('user', {})
        subscription_url = user.get('subscription_url', 'Не доступна')

        return BotTexts.SUBSCRIPTION_URL_MESSAGE.format(
            subscription_url=subscription_url
        )

    def format_trial_success(self, registration_data: Dict[str, Any]) -> str:
        """
        Форматирует сообщение об успешной регистрации триала.

        Args:
            registration_data: Данные регистрации от API

        Returns:
            Отформатированный текст
        """
        subscription = registration_data.get('subscription', {})
        end_date = subscription.get('end_date', 'N/A')

        return BotTexts.TRIAL_SUCCESS.format(end_date=end_date)