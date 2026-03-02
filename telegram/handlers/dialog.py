import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram.keyboards.inline import dialog_control_keyboard
from dialog_engine.dialog_state import DialogState
from services.case_service import process_dialog,check_diagnosis
router = Router(name="dialog")
logger = logging.getLogger(__name__)


@router.message(Command("finish"))
async def finish_dialog(msg: Message, state: FSMContext) -> None:
    logger.info("Finish command: user_id=%s", msg.from_user.id if msg.from_user else None)
    await state.clear()
    await msg.answer("✅ Диалог завершён командой /завершить")
    await msg.answer("Для нового кейса нажмите /start")


@router.message(Command("diagnosis"))
async def force_diagnosis(msg: Message, state: FSMContext) -> None:
    logger.info("Diagnosis command: user_id=%s", msg.from_user.id if msg.from_user else None)
    data = await state.get_data()
    if not data or "patient" not in data:
        await msg.answer("Сначала начните кейс! Нажмите /start")
        return
    await state.set_state(DialogState.waiting_diagnosis)
    await msg.answer("📝 Поставьте диагноз — напишите его текстом:")


@router.message(DialogState.waiting_question)
async def handle_dialog(msg: Message, state: FSMContext) -> None:
    user_id = msg.from_user.id if msg.from_user else None
    logger.info("Dialog message: user_id=%s, text=%r", user_id, msg.text)

    data = await state.get_data()
    engine = data.get("engine")
    if engine is None:
        await msg.answer("Произошла ошибка состояния. Начните новый кейс через /start")
        await state.clear()
        return

    answer = process_dialog(engine=engine, user_text=msg.text or "")
    await msg.answer(answer, reply_markup=dialog_control_keyboard())


@router.message(DialogState.waiting_diagnosis)
async def handle_diagnosis(msg: Message, state: FSMContext) -> None:
    user_id = msg.from_user.id if msg.from_user else None
    logger.info("Diagnosis message: user_id=%s, text=%r", user_id, msg.text)

    data = await state.get_data()
    patient = data.get("patient")
    card = data.get("card")

    if patient is None or card is None:
        await msg.answer("Произошла ошибка состояния. Начните новый кейс через /start")
        await state.clear()
        return

    result = check_diagnosis(
        user_text=msg.text or "",
        patient=patient,
        card=card,
    )

    await msg.answer(result.message_text)
    await msg.answer(result.rendered_card)
    await state.clear()
    await msg.answer("Диалог завершён. Для нового кейса нажмите /start")
