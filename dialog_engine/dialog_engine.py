import logging

from dialog_engine.dialog_state import DialogState
from giga.llm_response_generator import GigachatResponseGenerator
from dialog_engine.patient_card_manager import PatientCardManager
from models.entities.medical_card import MedicalCard
from models.entities.patient import Patient

logger = logging.getLogger(__name__)


class DialogEngine:

    def __init__(self, patient: Patient, card: MedicalCard) -> None:
        self.dialog_state = DialogState()
        self.patient_card_manager = PatientCardManager(patient, card)
        self.llm_generator = GigachatResponseGenerator(
            disease_name=patient.disease.name,
            complaints=patient.disease.complaints,
        )
        logger.info("DialogEngine initialized for patient %s", patient.fio)

    def process(self, text: str) -> str:
        self.dialog_state.add_to_history("user", text)

        if self.dialog_state.stage == "greeting":
            response = self._handle_greeting(text)
        else:
            response = self._generate_response(text)

        self.dialog_state.add_to_history("assistant", response)
        return response

    def _handle_greeting(self, text: str) -> str:
        additional = "Ты только что зашёл в кабинет врача. Это начало приёма."
        context = self.patient_card_manager.get_disease_context() + f"\n\nДополнительно: {additional}"
        response = self._call_llm(context)
        self.dialog_state.transition_stage("dialog")
        return response

    def _generate_response(self, text: str) -> str:
        context = self.patient_card_manager.get_disease_context()
        return self._call_llm(context)

    def _call_llm(self, context: str) -> str:
        recent = self.dialog_state.get_recent_history(20)
        return self.llm_generator.generate_response(context=context, dialog_messages=recent)

    def reset_dialog(self) -> None:
        self.dialog_state = DialogState()
        logger.info("Dialog reset")
