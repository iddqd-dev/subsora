from pydantic import BaseModel
from typing import Optional

class TelegramLoginData(BaseModel):
    """
    Схема для данных, получаемых от виджета Telegram Login.
    Поля должны точно соответствовать тому, что присылает твой Flutter-плагин.
    """
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str