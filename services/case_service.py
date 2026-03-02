import logging
import random
from dataclasses import dataclass

from services.diagnosis import check, similarity_score
from dialog_engine.dialog_engine import DialogEngine
from models.models import DiseaseType, MedicalCard, Patient
from models.patient_factory import create_patient

logger = logging.getLogger(__name__)


@dataclass
class CaseInitResult:
    patient: Patient
    card: MedicalCard
    engine: DialogEngine


@dataclass
class DiagnosisResult:
    is_correct: bool
    message_text: str
    rendered_card: str
    score: float = 0.0

class CaseRepository:
    """Создаёт доменные объекты. Единственное место где знает о patient_factory."""

    @staticmethod
    def build(disease_type: DiseaseType) -> CaseInitResult:
        patient = create_patient(disease_type)
        card = MedicalCard()
        engine = DialogEngine(patient=patient, card=card)
        logger.info("Case built: patient=%s, disease=%s", patient.fio, patient.disease.name)
        return CaseInitResult(patient=patient, card=card, engine=engine)

    @staticmethod
    def build_random() -> CaseInitResult:
        disease = random.choice(list(DiseaseType))
        logger.info("Starting random case: %s", disease)
        return CaseRepository.build(disease)

class StartCaseUseCase:
    """Запускает новый кейс по типу болезни или случайный."""

    def __init__(self, repo: CaseRepository) -> None:
        self._repo = repo

    def by_type(self, disease_type: DiseaseType) -> CaseInitResult:
        logger.info("Starting case by type: %s", disease_type)
        return self._repo.build(disease_type)

    def random(self) -> CaseInitResult:
        return self._repo.build_random()

class ProcessDialogUseCase:
    """Обрабатывает один ход диалога."""

    def execute(self, engine: DialogEngine, user_text: str) -> str:
        return engine.process(user_text)

class CheckDiagnosisUseCase:
    """Проверяет диагноз врача и заполняет карту."""

    def execute(self, user_text: str, patient: Patient, card: MedicalCard) -> DiagnosisResult:
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

# Фасад для обратной совместимости с хендлерами
# Хендлеры пока вызывают эти функции — менять их не нужно.
_repo = CaseRepository()
_start_case = StartCaseUseCase(_repo)
_process_dialog = ProcessDialogUseCase()
_check_diagnosis = CheckDiagnosisUseCase()

def start_random_case() -> CaseInitResult:
    return _start_case.random()

def start_case_by_type(disease_type: DiseaseType) -> CaseInitResult:
    return _start_case.by_type(disease_type)

def process_dialog(engine: DialogEngine, user_text: str) -> str:
    return _process_dialog.execute(engine, user_text)

def check_diagnosis(user_text: str, patient: Patient, card: MedicalCard) -> DiagnosisResult:
    return _check_diagnosis.execute(user_text, patient, card)

