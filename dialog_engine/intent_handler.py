from dialog_engine.patient_card_manager import PatientCardManager
from dialog_engine.experience_enricher import ExperienceEnricher

class IntentHandler:
    """Класс для обработки интентов"""

    def __init__(self, patient_card_manager: PatientCardManager, experience_enricher: ExperienceEnricher):
        self.patient_card_manager = patient_card_manager
        self.enricher = experience_enricher

    def process_intent(self, intent: str, text: str) -> str:
        """Обработать конкретный интент"""
        if intent == "complaints":
            return self._handle_complaints()
        elif intent == "anamnesis":
            return self._handle_anamnesis()
        elif intent == "diagnostics":
            return self._handle_diagnostics()
        elif intent == "diagnosis":
            return self._handle_diagnosis()
        return None

    def _handle_complaints(self) -> str:
        complaints = self.patient_card_manager.patient.disease.complaints
        self.patient_card_manager.update_complaints(complaints)
        complaints_text = ", ".join(complaints)
        enriched = self.enricher.enrich_complaints(
            self.patient_card_manager.patient.disease.name
        )
        return f"Из основных жалоб: {complaints_text}. {enriched}"

    def _handle_anamnesis(self) -> str:
        anamnesis = self.patient_card_manager.patient.disease.anamnesis
        self.patient_card_manager.update_anamnesis(anamnesis)
        anamnesis_text = ", ".join(anamnesis)
        enriched = self.enricher.enrich_anamnesis(
            self.patient_card_manager.patient.disease.name
        )
        return f"Если говорить о том, как всё началось: {anamnesis_text}. {enriched}"

    def _handle_diagnostics(self) -> str:
        diagnostics = self.patient_card_manager.patient.disease.diagnostics
        self.patient_card_manager.update_diagnostics(diagnostics)
        diag_text = ", ".join(diagnostics)
        enriched = self.enricher.enrich_diagnostics(
            self.patient_card_manager.patient.disease.name
        )
        return f"Из обследований: {diag_text}. {enriched}"

    def _handle_diagnosis(self) -> str:
        return "Я не врач, чтобы ставить диагноз. По моим симптомам - сильная жажда, частое мочеиспускание, слабость. Как вы думаете, что это может быть?"