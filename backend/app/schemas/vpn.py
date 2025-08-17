from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VpnStats(BaseModel):
    """
    Схема для статистики использования VPN, полученной из Marzban.
    """
    used_traffic: int = Field(..., description="Использованный трафик в байтах")
    data_limit: int = Field(..., description="Лимит трафика в байтах (0, если безлимит)")
    status: str = Field(..., description="Статус пользователя в Marzban (active, disabled, etc.)")
    online_at: Optional[datetime] = Field(None, description="Время последнего подключения")
    expire: Optional[int] = Field(None, description="Unix timestamp окончания подписки в Marzban")

    class Config:
        from_attributes = True