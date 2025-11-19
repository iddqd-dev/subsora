"""Хендлеры для работы с подписками и тарифами."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

    """
    plan_id = int(callback.data.split("_")[-1])

    # 1. Спрашиваем метод оплаты
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Банковская карта (РФ)", callback_data=f"pay_mock_{plan_id}"))
    builder.row(InlineKeyboardButton(text="💎 Crypto (USDT)", callback_data=f"pay_mock_{plan_id}"))
    builder.row(get_back_button(CallbackData.PLANS).inline_keyboard[0][0])

    await callback.message.edit_text(
        "Выберите способ оплаты:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_mock_"))
async def mock_payment_process(callback: CallbackQuery):
    """Симуляция процесса оплаты"""
    plan_id = int(callback.data.split("_")[-1])

    await callback.message.edit_text("⏳ Формирование счета...")

    # В реальном проекте здесь мы создаем ссылку на оплату (ЮKassa/Stripe)
    # И даем кнопку "Оплатить".

    # Т.к. у нас нет реальной платежки, делаем "Магию":
    # Мы используем логику триала, но подставляем нужный plan_id.
    # НО! Твой эндпоинт /register-trial жестко ищет тариф с именем 'пробный'.

    # ВАРИАНТ БЕЗ ИЗМЕНЕНИЯ БЭКЕНДА:
    # Просто пишем пользователю обратиться к администратору для покупки.

    await callback.message.edit_text(
        """💳 *Тестовый режим оплаты*

В данный момент автоматическая оплата находится в разработке.
Для покупки подписки напишите администратору: @admin\_username
Укажите ваш ID: `{}`
""".format(callback.from_user.id),
        reply_markup=get_back_button()
    )
    await callback.answer()