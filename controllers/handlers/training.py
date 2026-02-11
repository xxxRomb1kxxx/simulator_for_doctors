import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from controllers.keyboards.inline import training_menu
from controllers.states.dialog import DialogState
from models.entities.disease import DiseaseType
from services.case_service import CaseService


router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "training")
async def training(cb: CallbackQuery):
    logger.info("Training menu requested: user_id=%s", cb.from_user.id if cb.from_user else None)
    await cb.answer()
    await cb.message.answer(
        "🩺 Выберите заболевание для отработки:",
        reply_markup=training_menu()
    )
@router.callback_query(F.data == "control_case")
async def control_case(cb: CallbackQuery, state: FSMContext):
    logger.info("Control case requested: user_id=%s", cb.from_user.id if cb.from_user else None)

    await cb.answer()

    case = CaseService.start_random_case()

    await state.update_data(
        patient=case.patient,
        card=case.card,
        engine=case.engine,
    )

    await cb.message.answer(
        "🎯 Контрольный кейс начат!\n"
        "Вам достался пациент со случайным заболеванием. "
        "Попробуйте поставить правильный диагноз.\n\n"
        "Пациент заходит в кабинет..."
    )

    logger.debug("FSM data updated for control_case: %s", await state.get_data())

    await cb.message.answer("Добрый день, доктор. Можно войти на приём?")
    await state.set_state(DialogState.waiting_question)
    logger.info("State set to waiting_question for user_id=%s", cb.from_user.id if cb.from_user else None)

@router.callback_query(F.data.startswith("disease:"))
async def start_case(cb: CallbackQuery, state: FSMContext):
    logger.info(
        "Disease case requested: user_id=%s, data=%s",
        cb.from_user.id if cb.from_user else None,
        cb.data,
    )

    await cb.answer()
    disease_code = cb.data.split(":")[1]

    try:
        disease_type = DiseaseType(disease_code)
        case = CaseService.start_case_by_type(disease_type)
        logger.info(
            "Case started by disease: disease_code=%s, disease_type=%s, patient_fio=%s",
            disease_code,
            disease_type,
            getattr(case.patient, "fio", "unknown"),
        )
    except ValueError:
        logger.warning("Unknown disease type requested: %s", disease_code)
        await cb.message.answer("Ошибка: неизвестный тип заболевания")
        return

    await state.update_data(
        patient=case.patient,
        card=case.card,
        engine=case.engine
    )
    logger.debug("FSM data updated for start_case: %s", await state.get_data())

    await cb.message.answer("Диалог начат! Вы - врач, пациент заходит к вам в кабинет.")
    await cb.message.answer("Добрый день, доктор. Можно войти на приём?")
    await state.set_state(DialogState.waiting_question)
    logger.info("State set to waiting_question for user_id=%s", cb.from_user.id if cb.from_user else None)