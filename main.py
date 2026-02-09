import asyncio
from aiogram import Bot, Dispatcher

from config.settings import settings
from controllers.handlers import menu, training, dialog

async def main():
    bot = Bot(settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(menu.router)
    dp.include_router(training.router)
    dp.include_router(dialog.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
