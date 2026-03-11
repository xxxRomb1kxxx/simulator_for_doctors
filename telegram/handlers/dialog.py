import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram.keyboards.inline import dialog_control_keyboard
from dialog_engine.dialog_state import DialogState
from services.case_service import process_dialog, check_diagnosis
from services.kafka_service import (
    async_send_event,
    send_gigachat_error,
    TOPIC_DIALOG_LOGS,
    TOPIC_DIAGNOSIS_RESULTS,
)
from config import get_settings

router = Router(name="dialog")
logger = logging.getLogger(__name__)


def _kafka_enabled() -> bool:
    return get_settings().kafka_enabled


@router.message(Command("finish"))
async def finish_dialog(msg: Message, state: FSMContext) -> None:
    user_id = msg.from_user.id if msg.from_user else None
    if _kafka_enabled() and user_id:
        await async_send_event(TOPIC_DIALOG_LOGS, str(user_id), {
            "user_id": user_id,
            "event": "dialog_finished",
            "trigger": "command",
        })
    await state.clear()
    await msg.answer("✅ Диалог завершён командой /завершить")
    await msg.answer("Для нового кейса нажмите /start")


@router.message(Command("diagnosis"))
async def force_diagnosis(msg: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if not data or "patient" not in data:
        await msg.answer("Сначала начните кейс! Нажмите /start")
        return
    await state.set_state(DialogState.waiting_diagnosis)
    await msg.answer("📝 Поставьте диагноз — напишите его текстом:")


@router.message(DialogState.waiting_question)
async def handle_dialog(msg: Message, state: FSMContext) -> None:
    user_id = msg.from_user.id if msg.from_user else None

    data = await state.get_data()
    engine = data.get("engine")
    if engine is None:
        await msg.answer("Произошла ошибка состояния. Начните новый кейс через /start")
        await state.clear()
        return

    if _kafka_enabled() and user_id:
        await async_send_event(TOPIC_DIALOG_LOGS, str(user_id), {
            "user_id": user_id,
            "role": "doctor",
            "text": msg.text or "",
            "disease": engine.patient.disease.name,
        })

    try:
        answer = process_dialog(engine=engine, user_text=msg.text or "")
    except Exception as exc:
        logger.error("process_dialog failed: user_id=%s err=%s", user_id, exc)
        if _kafka_enabled() and user_id:
            send_gigachat_error(str(user_id), str(exc), {
                "disease": engine.patient.disease.name,
            })
        await msg.answer("Произошла ошибка при обращении к GigaChat. Попробуйте ещё раз.")
        return

    if _kafka_enabled() and user_id:
        await async_send_event(TOPIC_DIALOG_LOGS, str(user_id), {
            "user_id": user_id,
            "role": "patient",
            "text": answer,
            "disease": engine.patient.disease.name,
        })

    await msg.answer(answer, reply_markup=dialog_control_keyboard())


@router.message(DialogState.waiting_diagnosis)
async def handle_diagnosis(msg: Message, state: FSMContext) -> None:
    user_id = msg.from_user.id if msg.from_user else None

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

    if _kafka_enabled() and user_id:
        await async_send_event(TOPIC_DIAGNOSIS_RESULTS, str(user_id), {
            "user_id": user_id,
            "disease": patient.disease.name,
            "correct_diagnosis": patient.disease.correct_diagnosis,
            "user_diagnosis": msg.text or "",
            "score": round(result.score, 3),
            "is_correct": result.is_correct,
        })

    await msg.answer(result.message_text)
    await msg.answer(result.rendered_card)
    await state.clear()
    await msg.answer("Диалог завершён. Для нового кейса нажмите /start")