from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from controllers.keyboards.inline import main_menu

router = Router()

@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer("👋 Симулятор врача", reply_markup=main_menu())
