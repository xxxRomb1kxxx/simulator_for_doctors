from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from controllers.states.dialog import DialogState
from services.diagnosis_checker import check

router = Router()

@router.message(DialogState.waiting_question)
async def dialog(msg: Message, state: FSMContext):
    data = await state.get_data()
    engine = data["engine"]

    answer = engine.process(msg.text)
    await msg.answer(f"🧍‍♂️ Пациент: {answer}")

    if "Какой у меня диагноз" in answer:
        await state.set_state(DialogState.waiting_diagnosis)

@router.message(DialogState.waiting_diagnosis)
async def diagnosis(msg: Message, state: FSMContext):
    data = await state.get_data()
    patient = data["patient"]
    card = data["card"]

    card.diagnosis = msg.text

    if check(msg.text, patient.disease.correct_diagnosis):
        await msg.answer("✅ Диагноз верный!")
    else:
        await msg.answer(f"❌ Неверно. Правильно: {patient.disease.correct_diagnosis}")

    await msg.answer(card.render())
    await state.clear()
