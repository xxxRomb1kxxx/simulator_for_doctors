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
        if self.dialog_state.stage == "greeting":
            return self._handle_greeting_stage(text.lower())
        return self._generate_llm_response(text)

    def _handle_greeting_stage(self, text: str) -> str:
        self.dialog_state.transition_stage("dialog")
        # greeting_context = """
        # Ситуация: Ты только что зашел в кабинет врача.
        # Это начало приема. Врач тебя пригласил.
        # Будь вежливым, немного волнительным, представься.
        # """
        # doctor_question = "приглашаю" if any(w in text for w in ["проходи", "сад", "да"]) else "можно войти?"

        return self._generate_llm_response(
            text=text
        )

    def _generate_llm_response(self, text: str) -> str:
        context = self.patient_card_manager.get_disease_context()
        history = self.dialog_state.get_recent_history(10)
        response = self.llm_generator.generate_response(context, history, text)
        return response