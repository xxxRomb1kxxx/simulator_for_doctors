import logging
import random

from services.patient_factory import create_patient
from models.entities.medical_card import MedicalCard
from dialog_engine.dialog_engine import DialogEngine
from models.entities.disease import DiseaseType
from services.diagnosis_checker import check
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DialogResult:
    answer_text: str
    should_ask_diagnosis: bool
    prompt_text: str | None = None


@dataclass
class DiagnosisResult:
    is_correct: bool
    message_text: str
    rendered_card: str

@dataclass
class CaseInitResult:
    patient: object
    card: object
    engine: object

class CaseService:

    @staticmethod
    def start_random_case() -> CaseInitResult:
        disease = random.choice(list(DiseaseType))
        logger.info("Starting random case with disease: %s", disease)
        return CaseService._build_case(disease)

    @staticmethod
    def start_case_by_type(disease_type: DiseaseType) -> CaseInitResult:
        logger.info("Starting case by type: %s", disease_type)
        return CaseService._build_case(disease_type)

    @staticmethod
    def _build_case(disease_type: DiseaseType) -> CaseInitResult:
        patient = create_patient(disease_type)
        card = MedicalCard()
        engine = DialogEngine(patient, card)
        logger.info("Case built for patient=%s, disease=%s", patient.fio, patient.disease.name)

        return CaseInitResult(
            patient=patient,
            card=card,
            engine=engine
        )

    @staticmethod
    def process_dialog(engine: DialogEngine, user_text: str) -> DialogResult:
        answer = engine.process(user_text)
        logger.info("Processing dialog, user_text=%s", user_text)

        should_ask = (
            "что это может быть" in answer.lower()
            or "диагноз" in answer.lower()
        )
        logger.info("Dialog answer=%s, should_ask_diagnosis=%s", answer, should_ask)

        return DialogResult(
            answer_text=answer,
            should_ask_diagnosis=should_ask,
            prompt_text="Теперь поставьте диагноз (напишите его текстом):"
            if should_ask else None
        )

    @staticmethod
    def check_diagnosis(
        user_text: str,
        patient,
        card: MedicalCard
    ) -> DiagnosisResult:

        user_diagnosis = user_text.strip()
        card.diagnosis = user_diagnosis

        is_correct = check(
            user_diagnosis,
            patient.disease.correct_diagnosis
        )

        if is_correct:
            message = "Диагноз верный!"
        else:
            message = (
                f"Неверно. Правильный диагноз: "
                f"{patient.disease.correct_diagnosis}"
            )

        return DiagnosisResult(
            is_correct=is_correct,
            message_text=message,
            rendered_card=card.render()
        )




