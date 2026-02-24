import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from controllers.handlers.dialog import finish_dialog, force_diagnosis
from controllers.keyboards.inline import training_menu
from controllers.states.dialog import DialogState
from models.entities.disease import DiseaseType
from services.case_service import CaseService

router = Router(name="training")
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "training")
async def training(cb: CallbackQuery) -> None:
    logger.info("Training menu: user_id=%s", cb.from_user.id if cb.from_user else None)
    await cb.answer()
    await cb.message.answer(
        "🩺 Выберите заболевание для отработки:",
        reply_markup=training_menu(),
    )


@router.callback_query(F.data.in_({"cmd:diagnosis", "cmd:finish"}))
async def dialog_commands(cb: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает кнопки управления диалогом.
    ИСПРАВЛЕН БАГ оригинала: вызов force_diagnosis() / finish_dialog() без аргументов.
    """
    await cb.answer()
    # Создаём Message-like объект через cb.message для передачи в хендлеры
    if cb.data == "cmd:diagnosis":
        await force_diagnosis(cb.message, state)
    elif cb.data == "cmd:finish":
        await finish_dialog(cb.message, state)


@router.callback_query(F.data == "control_case")
async def control_case(cb: CallbackQuery, state: FSMContext) -> None:
    logger.info("Control case: user_id=%s", cb.from_user.id if cb.from_user else None)
    await cb.answer()

    case = CaseService.start_random_case()
    await state.update_data(patient=case.patient, card=case.card, engine=case.engine)
    await state.set_state(DialogState.waiting_question)

    await cb.message.answer(
        "🎯 <b>Контрольный кейс начат!</b>\n"
        "Вам достался пациент со случайным заболеванием. "
        "Попробуйте поставить правильный диагноз."
    )
    await cb.message.answer("Добрый день, доктор. Можно войти на приём?")
    logger.info("State → waiting_question for user_id=%s", cb.from_user.id if cb.from_user else None)


@router.callback_query(F.data.startswith("disease:"))
async def start_case(cb: CallbackQuery, state: FSMContext) -> None:
    user_id = cb.from_user.id if cb.from_user else None
    logger.info("Disease case: user_id=%s, data=%s", user_id, cb.data)
    await cb.answer()

    disease_code = cb.data.split(":", 1)[1]
    try:
        disease_type = DiseaseType(disease_code)
    except ValueError:
        logger.warning("Unknown disease type: %s", disease_code)
        await cb.message.answer("❌ Ошибка: неизвестный тип заболевания")
        return

    case = CaseService.start_case_by_type(disease_type)
    await state.update_data(patient=case.patient, card=case.card, engine=case.engine)
    await state.set_state(DialogState.waiting_question)

    logger.info(
        "Case started: disease=%s, patient=%s, user_id=%s",
        disease_type, case.patient.fio, user_id,
    )
    await cb.message.answer("Диалог начат! Вы — врач, пациент заходит в кабинет.")
    await cb.message.answer("Добрый день, доктор. Можно войти на приём?")
