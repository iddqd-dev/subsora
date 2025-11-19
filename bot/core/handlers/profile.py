"""Хендлеры для работы с профилем пользователя."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from ..api_client import api_client, UserNotFoundError, SubsoraApiClientError
from ..services.user_service import UserService
from ..constants import CallbackData
from ..texts import BotTexts
from ..keyboards.inline import get_profile_menu, get_trial_menu, get_plans_menu
from ..keyboards.inline import get_instruction_keyboard

logger = logging.getLogger(__name__)
router = Router()

# Создаем экземпляр сервиса
user_service = UserService(api_client)


@router.callback_query(F.data == CallbackData.PROFILE)
async def show_profile(callback: CallbackQuery):
    """Показывает профиль пользователя."""
    telegram_id = callback.from_user.id

    try:
        profile_data = await api_client.get_profile(telegram_id)

        # Форматируем текст через сервис
        text = user_service.format_profile_text(profile_data)

        # Проверяем наличие активной подписки для кнопок
        has_subscription = profile_data.get('active_subscription') is not None

        await callback.message.edit_text(
            text,
            reply_markup=get_profile_menu(has_subscription=has_subscription)
        )

    except UserNotFoundError:
        # Пользователь не найден - предлагаем триал
        await callback.message.edit_text(
            BotTexts.NOT_REGISTERED,
            reply_markup=get_trial_menu()
        )

    except SubsoraApiClientError as e:
        logger.error(f"API error for user {telegram_id}: {e}")
        await callback.message.edit_text(
            BotTexts.ERROR_GENERIC,
            reply_markup=get_trial_menu()
        )

    await callback.answer()


@router.callback_query(F.data == CallbackData.SUBSCRIPTION_URL)
async def show_subscription_url(callback: CallbackQuery):
    """Отправляет ссылку для подключения VPN."""
    telegram_id = callback.from_user.id

    try:
        profile_data = await api_client.get_profile(telegram_id)

        # Форматируем сообщение со ссылкой
        text = user_service.format_subscription_url(profile_data)

        # Отправляем новым сообщением (чтобы пользователь мог легко скопировать)
        await callback.message.answer(
            text,
            reply_markup=get_instruction_keyboard(),  # Кнопки скачивания приложений
            disable_web_page_preview=True
        )

        await callback.answer()

    except UserNotFoundError:
        await callback.answer("❌ Профиль не найден", show_alert=True)

    except SubsoraApiClientError as e:
        logger.error(f"Error getting subscription URL for {telegram_id}: {e}")
        await callback.answer("❌ Ошибка получения ссылки", show_alert=True)


@router.callback_query(F.data == CallbackData.TRIAL)
async def activate_trial(callback: CallbackQuery):
    """Активирует пробный период для пользователя."""
    user = callback.from_user
    await callback.message.edit_text("⏳ Проверяю доступность пробного периода...")

    try:
        registration_data = await api_client.register_trial(
            telegram_id=user.id,
            full_name=user.full_name,
            username=user.username
        )

        text = user_service.format_trial_success(registration_data)

        # Успех! Показываем профиль с кнопкой "Ссылка"
        await callback.message.edit_text(
            text,
            reply_markup=get_profile_menu(has_subscription=True)
        )

    except SubsoraApiClientError as e:
        # Обрабатываем нашу специальную ошибку
        if str(e) == "ALREADY_USED":
            await callback.message.edit_text(
                "❌ <b>Ошибка получения триала</b>\n\n"
                "Вы уже использовали пробный период или у вас была подписка ранее.\n"
                "Пожалуйста, выберите один из платных тарифов.",
                reply_markup=get_plans_menu(await api_client.get_available_plans()),
                parse_mode="HTML"
            )
        else:
            logger.error(f"Error activating trial for {user.id}: {e}")
            await callback.message.edit_text(
                "❌ Не удалось выдать пробный доступ.\nВозможно, технические работы. Попробуйте позже.",
                reply_markup=get_trial_menu()
            )

    await callback.answer()