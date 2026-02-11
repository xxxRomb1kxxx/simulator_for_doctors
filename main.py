import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.settings import settings
from controllers.handlers import menu, training, dialog
from config.logging import setup_logging

async def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Bot starting")
    bot = Bot(settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(menu.router)
    dp.include_router(training.router)
    dp.include_router(dialog.router)

    logger.info("Polling started")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
