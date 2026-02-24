"""
Точка входа приложения.

Исправления над оригиналом:
- set_bot_commands теперь вызывается при startup (в оригинале функция была, но нигде не вызывалась).
- Graceful shutdown — дожидаемся завершения текущих хендлеров.
- Redis FSM storage с fallback на Memory.
- Middleware регистрируется глобально.
- parse_mode=HTML (оригинал использовал Markdown в одних местах и HTML в других — непоследовательно).
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.logging import setup_logging
from config.settings import get_settings
from controllers.handlers import dialog, menu, training
from controllers.keyboards.inline import set_bot_commands
from middlewares.logging import LoggingMiddleware

logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    # Пробуем Redis, при недоступности — MemoryStorage
    try:
        from aiogram.fsm.storage.redis import RedisStorage

        settings = get_settings()
        storage = RedisStorage.from_url(settings.redis_url)
        logger.info("FSM storage: Redis (%s)", settings.redis_url)
    except Exception as e:
        logger.warning("Redis unavailable (%s), using MemoryStorage", e)
        storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    # Глобальный middleware
    dp.update.middleware(LoggingMiddleware())

    # Роутеры (порядок важен: dialog последним, чтобы Command-фильтры имели приоритет)
    dp.include_router(menu.router)
    dp.include_router(training.router)
    dp.include_router(dialog.router)

    return dp


async def on_startup(bot: Bot) -> None:
    me = await bot.get_me()
    await set_bot_commands(bot)  # <-- Исправлен баг оригинала: команды никогда не регистрировались
    logger.info("Bot started: @%s (id=%d)", me.username, me.id)


async def on_shutdown(bot: Bot) -> None:
    logger.info("Bot shutting down...")
    await bot.session.close()


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = build_dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
