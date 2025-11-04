"""Хендлер команды /start и главного меню."""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from ..constants import CallbackData
from ..texts import BotTexts
from ..keyboards.inline import get_main_menu

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработка команды /start."""
    logger.info(f"User {message.from_user.id} started the bot")

    await message.answer(
        BotTexts.WELCOME,
        reply_markup=get_main_menu()
    )


@router.callback_query(F.data == CallbackData.BACK_TO_MENU)
async def back_to_main_menu(callback: CallbackQuery):
    """Возврат в главное меню."""
    await callback.message.edit_text(
        BotTexts.WELCOME,
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработка команды /help."""
    help_text = """📚 *Помощь по боту Subsora*

/start - Главное меню
/help - Это сообщение

*Функции бота:*
• Просмотр профиля и подписки
• Получение ссылки для VPN
• Покупка и продление подписки
• Связь с поддержкой

По всем вопросам: @subsora_support"""

    await message.answer(help_text)