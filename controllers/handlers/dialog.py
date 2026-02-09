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
    await msg.answer(f"{answer}")

    if "что это может быть" in answer.lower() or "диагноз" in answer.lower():
        await state.set_state(DialogState.waiting_diagnosis)
        await msg.answer("Теперь поставьте диагноз (напишите его текстом):")


@router.message(DialogState.waiting_diagnosis)
async def diagnosis(msg: Message, state: FSMContext):
    data = await state.get_data()
    patient = data["patient"]
    card = data["card"]

    user_diagnosis = msg.text.strip()
    card.diagnosis = user_diagnosis

    if check(user_diagnosis, patient.disease.correct_diagnosis):
        await msg.answer("Диагноз верный!")
    else:
        await msg.answer(f"Неверно. Правильный диагноз: {patient.disease.correct_diagnosis}")

    await msg.answer(card.render())

    await state.clear()
    await msg.answer("Диалог завершён. Для нового кейса нажмите /start")