import hashlib
import hmac
from typing import Dict, Any


def validate_telegram_hash(data: Dict[str, Any], bot_token: str) -> bool:
    """
    Проверяет подлинность данных, полученных от Telegram Login Widget.
    """
    if 'hash' not in data:
        return False

    # Собираем все поля, кроме 'hash', в одну строку
    data_check_string_parts = []
    for key, value in sorted(data.items()):
        if key != 'hash' and value is not None:
            data_check_string_parts.append(f"{key}={value}")

    data_check_string = "\n".join(data_check_string_parts)

    # Создаем секретный ключ из токена бота
    secret_key = hashlib.sha256(bot_token.encode()).digest()

    # Вычисляем наш HMAC-хэш
    calculated_hash = hmac.new(
        secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Сравниваем наш хэш с тем, что пришел от Telegram
    return calculated_hash == data['hash']
