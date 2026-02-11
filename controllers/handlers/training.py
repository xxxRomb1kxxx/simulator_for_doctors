from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from controllers.keyboards.inline import training_menu
from controllers.states.dialog import DialogState
from models.entities.disease import DiseaseType
from services.case_service import CaseService


router = Router()


@router.callback_query(F.data == "training")
async def training(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(
        "🩺 Выберите заболевание для отработки:",
        reply_markup=training_menu()
    )
@router.callback_query(F.data == "control_case")
async def control_case(cb: CallbackQuery, state: FSMContext):

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
    await cb.message.answer("Добрый день, доктор. Можно войти на приём?")
    await state.set_state(DialogState.waiting_question)

@router.callback_query(F.data.startswith("disease:"))
async def start_case(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    disease_code = cb.data.split(":")[1]

    try:
        disease_type = DiseaseType(disease_code)
        case = CaseService.start_case_by_type(disease_type)
    except ValueError:
        await cb.message.answer("Ошибка: неизвестный тип заболевания")
        return

    await state.update_data(
        patient=case.patient,
        card=case.card,
        engine=case.engine
    )

    await cb.message.answer("Диалог начат! Вы - врач, пациент заходит к вам в кабинет.")
    await cb.message.answer("Добрый день, доктор. Можно войти на приём?")
    await state.set_state(DialogState.waiting_question)