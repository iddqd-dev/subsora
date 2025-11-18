"""Inline клавиатуры для бота."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..constants import CallbackData, ButtonText


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=ButtonText.PROFILE,
            callback_data=CallbackData.PROFILE
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=ButtonText.PLANS,
            callback_data=CallbackData.PLANS
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=ButtonText.SUPPORT,
            callback_data=CallbackData.SUPPORT
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=ButtonText.REFERRALS,
            callback_data=CallbackData.REFERRALS
        )
    )
    return builder.as_markup()


def get_profile_menu(has_subscription: bool = False) -> InlineKeyboardMarkup:
    """Меню профиля пользователя."""
    builder = InlineKeyboardBuilder()

    if has_subscription:
        builder.row(
            InlineKeyboardButton(
                text=ButtonText.SUBSCRIPTION_URL,
                callback_data=CallbackData.SUBSCRIPTION_URL
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=ButtonText.BACK_TO_MENU,
            callback_data=CallbackData.BACK_TO_MENU
        )
    )
    return builder.as_markup()


def get_trial_menu() -> InlineKeyboardMarkup:
    """Меню для незарегистрированных пользователей."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=ButtonText.GET_TRIAL,
            callback_data=CallbackData.TRIAL
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=ButtonText.BACK_TO_MENU,
            callback_data=CallbackData.BACK_TO_MENU
        )
    )
    return builder.as_markup()


def get_plans_menu(plans: list = None) -> InlineKeyboardMarkup:
    """Меню выбора тарифного плана."""
    builder = InlineKeyboardBuilder()

    if plans:
        for plan in plans:
            builder.row(
                InlineKeyboardButton(
                    text=f"{plan['name']} - {plan['price']} ₽",
                    callback_data=CallbackData.BUY_PLAN.format(plan_id=plan['id'])
                )
            )

    builder.row(
        InlineKeyboardButton(
            text=ButtonText.BACK_TO_MENU,
            callback_data=CallbackData.BACK_TO_MENU
        )
    )
    return builder.as_markup()


def get_back_button(callback_data: str = CallbackData.BACK_TO_MENU) -> InlineKeyboardMarkup:
    """Простая кнопка "Назад"."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=ButtonText.BACK,
            callback_data=callback_data
        )
    )
    return builder.as_markup()

def get_instruction_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🍏 iOS (V2Box)", url="https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690"),
        InlineKeyboardButton(text="🤖 Android (v2rayNG)", url="https://play.google.com/store/apps/details?id=com.v2ray.ang")
    )
    builder.row(
        InlineKeyboardButton(text="💻 Windows (Hiddify)", url="https://github.com/hiddify/hiddify-next/releases")
    )
    builder.row(InlineKeyboardButton(text="🗑 Скрыть", callback_data="delete_msg"))
    return builder.as_markup()