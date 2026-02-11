from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from controllers.states.dialog import DialogState
from services.case_service import CaseService

router = Router()


@router.message(DialogState.waiting_question)
async def dialog(msg: Message, state: FSMContext):
    data = await state.get_data()

    result = CaseService.process_dialog(
        engine=data["engine"],
        user_text=msg.text
    )

    await msg.answer(result.answer_text)

    if result.should_ask_diagnosis:
        await state.set_state(DialogState.waiting_diagnosis)
        await msg.answer(result.prompt_text)


@router.message(DialogState.waiting_diagnosis)
async def diagnosis(msg: Message, state: FSMContext):
    data = await state.get_data()

    result = CaseService.check_diagnosis(
        user_text=msg.text,
        patient=data["patient"],
        card=data["card"]
    )

    await msg.answer(result.message_text)
    await msg.answer(result.rendered_card)

    await state.clear()
    await msg.answer("Диалог завершён. Для нового кейса нажмите /start")