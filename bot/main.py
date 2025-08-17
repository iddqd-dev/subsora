import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from core.api_client import settings, api_client
from core.handlers import router as main_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    # Создаем объекты бота и диспетчера
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Включаем наш роутер с хендлерами
    dp.include_router(main_router)

    # Запускаем поллинг
    print("Bot is starting...")
    await dp.start_polling(bot)

    # Закрываем сессию API-клиента при остановке
    await api_client.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
