import logging
from dialog_engine.dialog_state import DialogState
from dialog_engine.llm_response_generator import LLMResponseGenerator
from dialog_engine.patient_card_manager import PatientCardManager
from models.entities.patient import Patient



logger = logging.getLogger(__name__)

class DialogEngine:

    def __init__(self, patient: Patient, card):
        self.dialog_state = DialogState()
        self.patient_card_manager = PatientCardManager(patient, card)
        self.llm_generator = LLMResponseGenerator(
            patient.disease.name,
            patient.disease.complaints
        )
        logger.info("DialogEngine initialized for patient %s", patient.fio)

    def process(self, text: str) -> str:
        """Обрабатывает сообщение от врача и возвращает ответ пациента"""
        self.dialog_state.add_to_history("user", text)
        if self.dialog_state.stage == "greeting":
            response = self._handle_greeting_stage(text)
        else:
            response = self._generate_llm_response(text)
        self.dialog_state.add_to_history("assistant", response)

        return response

    def _handle_greeting_stage(self, text: str) -> str:
        greeting_context = "Ты только что зашел в кабинет врача. Это начало приема."
        response = self._generate_llm_response(text, additional_context=greeting_context)
        self.dialog_state.transition_stage("dialog")

        return response

    def _generate_llm_response(self, text: str, additional_context: str = "") -> str:
        disease_context = self.patient_card_manager.get_disease_context()
        if additional_context:
            disease_context += f"\n\nДополнительный контекст: {additional_context}"
        recent_history = self.dialog_state.get_recent_history(20)
        response = self.llm_generator.generate_response(
            context=disease_context,
            dialog_messages=recent_history
        )

        return response

    def reset_dialog(self):
        self.dialog_state = DialogState()
        logger.info("Dialog reset completed")