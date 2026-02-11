import logging
from dialog_engine.patient_card_manager import PatientCardManager
from dialog_engine.experience_enricher import ExperienceEnricher

logger = logging.getLogger(__name__)

class IntentHandler:

    def __init__(self, patient_card_manager: PatientCardManager, experience_enricher: ExperienceEnricher):
        self.patient_card_manager = patient_card_manager
        self.enricher = experience_enricher
        logger.info(
            "IntentHandler initialized for patient=%s, disease=%s",
            getattr(self.patient_card_manager.patient, "fio", "unknown"),
            getattr(self.patient_card_manager.patient.disease, "name", "unknown"),
        )

    def process_intent(self, intent: str, text: str) -> str:
        logger.info("Processing intent=%s, text=%s", intent, text)
        if intent == "complaints":
            return self._handle_complaints()
        elif intent == "anamnesis":
            return self._handle_anamnesis()
        elif intent == "diagnostics":
            return self._handle_diagnostics()
        elif intent == "diagnosis":
            return self._handle_diagnosis()
        else:
            logger.warning("Unknown intent: %s", intent)
            return None

    def _handle_complaints(self) -> str:
        complaints = self.patient_card_manager.patient.disease.complaints
        logger.debug("Complaints before update: %s", complaints)

        self.patient_card_manager.update_complaints(complaints)
        complaints_text = ", ".join(complaints)
        enriched = self.enricher.enrich_complaints(
            self.patient_card_manager.patient.disease.name
        )
        response = f"Из основных жалоб: {complaints_text}. {enriched}"
        logger.debug("Complaints response: %s", response)
        return response

    def _handle_anamnesis(self) -> str:
        anamnesis = self.patient_card_manager.patient.disease.anamnesis
        logger.debug("Anamnesis before update: %s", anamnesis)

        self.patient_card_manager.update_anamnesis(anamnesis)
        anamnesis_text = ", ".join(anamnesis)
        enriched = self.enricher.enrich_anamnesis(
            self.patient_card_manager.patient.disease.name
        )
        response = f"Если говорить о том, как всё началось: {anamnesis_text}. {enriched}"
        logger.debug("Anamnesis response: %s", response)
        return response

    def _handle_diagnostics(self) -> str:
        diagnostics = self.patient_card_manager.patient.disease.diagnostics
        logger.debug("Diagnostics before update: %s", diagnostics)
        self.patient_card_manager.update_diagnostics(diagnostics)
        diag_text = ", ".join(diagnostics)
        enriched = self.enricher.enrich_diagnostics(
            self.patient_card_manager.patient.disease.name
        )
        response = f"Из обследований: {diag_text}. {enriched}"
        logger.debug("Diagnostics response: %s", response)
        return response

    def _handle_diagnosis(self) -> str:
        response = (
            "Я не врач, чтобы ставить диагноз. По моим симптомам - сильная жажда, "
            "частое мочеиспускание, слабость. Как вы думаете, что это может быть?"
        )
        logger.info("Diagnosis question response sent")
        return response