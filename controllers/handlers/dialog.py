import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from controllers.states.dialog import DialogState
from services.case_service import CaseService

router = Router()
logger = logging.getLogger(__name__)

@router.message(DialogState.waiting_question)
async def dialog(msg: Message, state: FSMContext):
    logger.info(
        "Dialog message received: user_id=%s, text=%s, state=%s",
        msg.from_user.id if msg.from_user else None,
        msg.text,
        "waiting_question",
    )

    data = await state.get_data()

    result = CaseService.process_dialog(
        engine=data["engine"],
        user_text=msg.text
    )
    logger.info(
        "Dialog processed: answer_text=%s, should_ask_diagnosis=%s",
        result.answer_text,
        result.should_ask_diagnosis,
    )

    await msg.answer(result.answer_text)

    if result.should_ask_diagnosis:
        await state.set_state(DialogState.waiting_diagnosis)
        logger.info(
            "State changed to waiting_diagnosis for user_id=%s",
            msg.from_user.id if msg.from_user else None,
        )
        await msg.answer(result.prompt_text)


@router.message(DialogState.waiting_diagnosis)
async def diagnosis(msg: Message, state: FSMContext):
    logger.info(
        "Diagnosis message received: user_id=%s, text=%s, state=%s",
        msg.from_user.id if msg.from_user else None,
        msg.text,
        "waiting_diagnosis",
    )

    data = await state.get_data()
    logger.debug("FSM data (waiting_diagnosis): %s", data)

    result = CaseService.check_diagnosis(
        user_text=msg.text,
        patient=data["patient"],
        card=data["card"]
    )
    logger.info(
        "Diagnosis checked: is_correct=%s, message_text=%s",
        result.is_correct,
        result.message_text,
    )

    await msg.answer(result.message_text)
    await msg.answer(result.rendered_card)

    await state.clear()
    logger.info("State cleared for user_id=%s", msg.from_user.id if msg.from_user else None)
    await msg.answer("Диалог завершён. Для нового кейса нажмите /start")