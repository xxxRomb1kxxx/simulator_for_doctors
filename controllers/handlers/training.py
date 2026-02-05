from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from controllers.keyboards.inline import training_menu
from controllers.states.dialog import DialogState
from services.patient_factory import create_patient
from models.entities.medical_card import MedicalCard
from services.dialog_engine import DialogEngine
from models.entities.disease import DiseaseType

router = Router()

@router.callback_query(F.data == "training")
async def training(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(
        "Выберите заболевание:",
        reply_markup=training_menu()
    )

@router.callback_query(F.data.startswith("disease:"))
async def start_case(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    disease_code = cb.data.split(":")[1]
    disease_type = DiseaseType(disease_code)

    patient = create_patient(disease_type)
    card = MedicalCard()
    engine = DialogEngine(patient, card)

    await state.update_data(
        patient=patient,
        card=card,
        engine=engine
    )

    await cb.message.answer("Пациент: Можно войти?")
    await state.set_state(DialogState.waiting_question)
