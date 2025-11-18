import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from ..api_client import api_client, SubsoraApiClientError
from ..constants import CallbackData
from ..keyboards.inline import get_back_button

router = Router()


@router.callback_query(F.data == CallbackData.REFERRALS)
async def show_referrals(callback: CallbackQuery):
    tg_id = callback.from_user.id
    try:
        # Используем get_profile, так как там уже есть referral_code
        data = await api_client.get_profile(tg_id)
        user = data.get('user', {})
        code = user.get('referral_code', 'Ошибка')

        # Формируем реферальную ссылку (для start payload)
        bot_username = (await callback.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={code}"

        text = f"""👥 *Реферальная программа*

Приглашайте друзей и получайте скидки!

🔑 *Ваш код:* `{code}`
🔗 *Ваша ссылка:*
`{ref_link}`

🎁 *Бонусы:*
• 1 друг: 5% скидка
• 3 друга: 15% скидка
• 10 друзей: 30% скидка
"""
        await callback.message.edit_text(text, reply_markup=get_back_button())

    except SubsoraApiClientError:
        await callback.answer("Ошибка получения данных", show_alert=True)

    await callback.answer()
