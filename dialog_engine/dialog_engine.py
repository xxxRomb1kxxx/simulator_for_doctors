import logging
from dialog_engine.dialog_state import DialogState
from dialog_engine.experience_enricher import ExperienceEnricher
from dialog_engine.intent_handler import IntentHandler
from dialog_engine.llm_response_generator import LLMResponseGenerator
from dialog_engine.patient_card_manager import PatientCardManager
from models.entities.patient import Patient
from models.intents.intents import detect_intent


logger = logging.getLogger(__name__)

class DialogEngine:
    """Главный класс для управления диалогом (рефакторинг)"""

    def __init__(self, patient: Patient, card):
        self.dialog_state = DialogState()
        self.patient_card_manager = PatientCardManager(patient, card)
        self.experience_enricher = ExperienceEnricher()
        self.intent_handler = IntentHandler(self.patient_card_manager, self.experience_enricher)
        self.llm_generator = LLMResponseGenerator(
            patient.disease.name,
            patient.disease.complaints
        )
        logger.info("DialogEngine initialized for patient %s", patient.fio)

    def process(self, text: str) -> str:
        """Обработать пользовательский ввод"""
        text_lower = text.lower()
        self.dialog_state.add_to_history(text)

        if self.dialog_state.stage == "greeting":
            return self._handle_greeting_stage(text_lower)


        intent = detect_intent(text_lower)

        if intent in ["complaints", "anamnesis", "diagnostics", "diagnosis"]:
            response = self.intent_handler.process_intent(intent, text_lower)
        else:
            response = self._generate_llm_response(text_lower)

        self.dialog_state.add_to_history(response)
        return response

    def _handle_greeting_stage(self, text: str) -> str:
        """Обработка стадии приветствия"""
        if any(w in text for w in ["проходи", "сад", "да", "можно", "входите"]):
            self.dialog_state.transition_stage("dialog")
            response = "Здравствуйте, доктор. Спасибо, что приняли меня. У меня есть некоторые проблемы со здоровьем, которые меня беспокоят."
        else:
            response = "Добрый день, доктор. Можно войти на приём?"

        self.dialog_state.add_to_history(response)
        return response

    def _generate_llm_response(self, text: str) -> str:
        """Сгенерировать ответ через LLM"""
        context = self.patient_card_manager.get_disease_context()
        history = self.dialog_state.get_recent_history(10)
        response = self.llm_generator.generate_response(context, history, text)
        return response