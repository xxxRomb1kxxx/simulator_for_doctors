import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from controllers.keyboards.inline import get_main_kb, main_menu, training_menu

router = Router(name="menu")
logger = logging.getLogger(__name__)

_WELCOME_TEXT = (
    "👨‍⚕️ <b>СИМУЛЯТОР ДЛЯ ВРАЧЕЙ BFU</b>\n\n"
    "🎯 <b>Функционал бота:</b>\n"
    "• 🏥 <b>Тренировка</b> — интерактивные кейсы с пациентами\n"
    "• 🤖 <b>Реалистичный диалог</b> — GigaChat имитирует пациента\n"
    "• 🩺 <b>Проверка диагноза</b> — автоматическая оценка правильности\n\n"
    "📋 <b>Управление:</b>\n"
    "• /finish — выйти из диалога в любой момент\n"
    "• /diagnosis  — сразу перейти к постановке диагноза\n"
    "• /start — главное меню\n\n"
    "<b>Выберите режим тренировки:</b>"
)

_HELP_TEXT = (
    "📖 <b>Как пользоваться симулятором:</b>\n\n"
    "1️⃣ <b>Начните</b> — /start → «🏥 Тренажер»\n"
    "2️⃣ <b>Выберите</b> болезнь из списка\n"
    "3️⃣ <b>Опрашивайте</b> пациента (обычный текст)\n"
    "4️⃣ <b>Завершите</b> — /диагноз или /завершить\n"
    "5️⃣ <b>Проверьте</b> диагноз — напишите название болезни\n\n"
    "✅ Готово к тренировке!"
)


@router.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    await msg.answer(_WELCOME_TEXT, reply_markup=get_main_kb())


@router.callback_query(F.data == "start")
async def cb_start(cb: CallbackQuery) -> None:
    await cb.answer()
    await cb.message.answer(_WELCOME_TEXT, reply_markup=main_menu())


@router.message(F.text == "🏥 Тренажер")
async def trainer_button(msg: Message) -> None:
    logger.info("Trainer button: user_id=%s", msg.from_user.id if msg.from_user else None)
    await msg.answer("🩺 <b>Выберите заболевание для отработки:</b>", reply_markup=training_menu())


@router.message(F.text == "ℹ️ Помощь")
@router.message(Command("help"))
async def cmd_help(msg: Message) -> None:
    await msg.answer(_HELP_TEXT)
