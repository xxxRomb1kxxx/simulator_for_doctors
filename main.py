import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import setup_logging, get_settings
from telegram.handlers import dialog, menu, training
from telegram.keyboards.inline import set_bot_commands
from middlewares.logging import LoggingMiddleware

logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    dp.update.middleware(LoggingMiddleware())
    dp.include_router(menu.router)
    dp.include_router(training.router)
    dp.include_router(dialog.router)
    return dp

async def on_startup(bot: Bot) -> None:
    me = await bot.get_me()
    await set_bot_commands(bot)
    logger.info("Bot started: @%s (id=%d)", me.username, me.id)

async def on_shutdown(bot: Bot) -> None:
    logger.info("Bot shutting down...")
    settings = get_settings()
    if settings.kafka_enabled:
        try:
            from services.kafka_service import flush_producer
            flush_producer()
        except Exception as exc:
            logger.warning("Kafka flush failed on shutdown: %s", exc)
    await bot.session.close()

async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    bot = Bot(
        token=settings.telegram.bot_token,
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
