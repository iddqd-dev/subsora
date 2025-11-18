"""Константы для бота."""


class CallbackData:
    """Callback data для inline кнопок."""
    # Главное меню
    MAIN_MENU = "main_menu"
    PROFILE = "profile"
    PLANS = "plans"
    SUPPORT = "support"

    # Профиль
    SUBSCRIPTION_URL = "subscription_url"
    TRIAL = "get_trial"

    # Подписки
    BUY_PLAN = "buy_plan_{plan_id}"  # Используется с .format()

    # Навигация
    BACK_TO_MENU = "back_to_menu"
    BACK_TO_PROFILE = "back_to_profile"

    # Реферальная система
    REFERRALS = "referrals"

class ButtonText:
    """Тексты кнопок."""
    PROFILE = "👤 Личный кабинет"
    PLANS = "💳 Тарифы и подписки"
    SUPPORT = "💬 Поддержка"
    SUBSCRIPTION_URL = "🔗 Ссылка подключения"
    GET_TRIAL = "🎁 Получить триал"
    BACK = "🔙 Назад"
    BACK_TO_MENU = "🏠 Главное меню"
    REFERRALS = "👥 Рефералы"