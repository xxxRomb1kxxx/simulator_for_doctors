import logging
import random
from dataclasses import dataclass
from typing import Optional

from dialog_engine.dialog_engine import DialogEngine
from models.entities.disease import DiseaseType
from models.entities.medical_card import MedicalCard
from models.entities.patient import Patient
from services.diagnosis_checker import check, similarity_score
from services.patient_factory import create_patient

logger = logging.getLogger(__name__)


@dataclass
class DialogResult:
    answer_text: str
    should_ask_diagnosis: bool = False
    prompt_text: Optional[str] = None


@dataclass
class DiagnosisResult:
    is_correct: bool
    message_text: str
    rendered_card: str
    score: float = 0.0


@dataclass
class CaseInitResult:
    patient: Patient
    card: MedicalCard
    engine: DialogEngine


class CaseService:

    @staticmethod
    def start_random_case() -> CaseInitResult:
        disease = random.choice(list(DiseaseType))
        logger.info("Starting random case: %s", disease)
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
        logger.info("Case built: patient=%s, disease=%s", patient.fio, patient.disease.name)
        return CaseInitResult(patient=patient, card=card, engine=engine)

    @staticmethod
    def process_dialog(engine: DialogEngine, user_text: str) -> DialogResult:
        """
        Обрабатывает сообщение врача, возвращает ответ пациента.
        Решение о переходе к диагнозу — ТОЛЬКО через FSM-команды (/диагноз),
        не через text-matching здесь.
        """
        answer = engine.process(user_text)
        return DialogResult(answer_text=answer, should_ask_diagnosis=False)

    @staticmethod
    def check_diagnosis(
        user_text: str, patient: Patient, card: MedicalCard
    ) -> DiagnosisResult:
        user_diagnosis = user_text.strip()
        card.diagnosis = user_diagnosis

        correct = patient.disease.correct_diagnosis
        is_correct = check(user_diagnosis, correct)
        score = similarity_score(user_diagnosis, correct)

        if is_correct:
            message = f"✅ <b>Диагноз верный!</b>\nПоставлено: {user_diagnosis}"
        else:
            message = (
                f"❌ <b>Неверно.</b>\n"
                f"Ваш диагноз: {user_diagnosis}\n"
                f"Правильный диагноз: <b>{correct}</b>\n"
                f"Схожесть: {score:.0%}"
            )

        return DiagnosisResult(
            is_correct=is_correct,
            message_text=message,
            rendered_card=card.render(),
            score=score,
        )
