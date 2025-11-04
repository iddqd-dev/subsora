
"""Хендлеры для поддержки пользователей."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from ..constants import CallbackData
from ..texts import BotTexts
from ..keyboards.inline import get_back_button

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == CallbackData.SUPPORT)
async def show_support(callback: CallbackQuery):
    """Показывает информацию о поддержке."""
    await callback.message.edit_text(
        BotTexts.SUPPORT_MESSAGE,
        reply_markup=get_back_button()
    )
    await callback.answer()