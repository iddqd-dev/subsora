"""Хендлеры для работы с подписками и тарифами."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from ..api_client import api_client, SubsoraApiClientError
from ..constants import CallbackData
from ..texts import BotTexts
from ..keyboards.inline import get_plans_menu, get_back_button

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == CallbackData.PLANS)
async def show_plans(callback: CallbackQuery):
    """Показывает список доступных тарифов."""
    try:
        # Получаем список тарифов от API
        plans = await api_client.get_available_plans()

        if not plans:
            await callback.message.edit_text(
                "❌ Тарифы временно недоступны. Попробуйте позже.",
                reply_markup=get_back_button()
            )
            await callback.answer()
            return

        # Формируем текст со списком тарифов
        text_parts = [BotTexts.PLANS_LIST]

        for plan in plans:
            plan_text = BotTexts.PLAN_ITEM.format(
                name=plan.get('name', 'N/A'),
                price=plan.get('price', 0),
                duration=plan.get('duration_days', 30),
                description=plan.get('description', 'Нет описания')
            )
            text_parts.append(plan_text)

        text = "\n".join(text_parts)

        await callback.message.edit_text(
            text,
            reply_markup=get_plans_menu(plans)
        )

    except SubsoraApiClientError as e:
        logger.error(f"Error getting plans: {e}")
        await callback.message.edit_text(
            BotTexts.ERROR_GENERIC,
            reply_markup=get_back_button()
        )

    await callback.answer()


@router.callback_query(F.data.startswith("buy_plan_"))
async def process_plan_purchase(callback: CallbackQuery):
    """
    Обрабатывает выбор тарифа для покупки.

    TODO: Интеграция с платёжной системой
    """
    plan_id = callback.data.split("_")[-1]

    # Временная заглушка
    await callback.answer(
        "💳 Оплата временно недоступна. Функция в разработке.",
        show_alert=True
    )

    logger.info(f"User {callback.from_user.id} attempted to buy plan {plan_id}")

    # TODO: Здесь будет логика:
    # 1. Создание счёта на оплату
    # 2. Генерация ссылки на оплату (ЮKassa, Stripe и т.д.)
    # 3. Перевод пользователя в состояние ожидания оплаты
    # 4. Webhook от платёжной системы о статусе оплаты
    # 5. Активация подписки после успешной оплаты