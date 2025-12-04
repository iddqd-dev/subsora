import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings
from core.api_client import api_client
from core.handlers import start, profile, subscription, support

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    """Главная функция запуска бота."""
    # Создаем бота с дефолтным Markdown парсингом
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()

    # Регистрируем роутеры (порядок важен!)
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(subscription.router)
    dp.include_router(support.router)

    logger.info("Bot is starting...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await api_client.close()
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")

# Just CI trigger 4 build docker image
