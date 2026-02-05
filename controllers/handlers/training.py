from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from controllers.keyboards.inline import training_menu
from controllers.states.dialog import DialogState
from services.patient_factory import create_appendicitis_patient
from models.entities.medical_card import MedicalCard
from services.dialog_engine import DialogEngine

router = Router()

@router.callback_query(lambda c: c.data == "training")
async def training(cb: CallbackQuery):
    await cb.message.answer("Выберите заболевание:", reply_markup=training_menu())

@router.callback_query(lambda c: c.data == "appendicitis")
async def start_case(cb: CallbackQuery, state: FSMContext):
    patient = create_appendicitis_patient()
    card = MedicalCard()
    engine = DialogEngine(patient, card)

    await state.update_data(patient=patient, card=card, engine=engine)
    await cb.message.answer("🧍‍♂️ Пациент: Можно войти?")
    await state.set_state(DialogState.waiting_question)
