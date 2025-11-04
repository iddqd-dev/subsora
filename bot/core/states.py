"""FSM состояния для бота."""
from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """Состояния пользователя в боте."""
    main_menu = State()
    profile_view = State()
    subscription_select = State()
    payment_pending = State()
    support_chat = State()