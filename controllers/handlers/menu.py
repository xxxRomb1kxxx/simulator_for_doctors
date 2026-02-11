import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from controllers.keyboards.inline import main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def start(msg: Message):
    logger.info("Received /start from user_id=%s", msg.from_user.id if msg.from_user else None)
    await msg.answer("Симулятор врача", reply_markup=main_menu())
