import logging
from typing import Any

from giga.llm_response_generator import GigachatResponseGenerator
from models.models import MedicalCard, Patient

logger = logging.getLogger(__name__)


class DialogEngine:
    """Управляет диалогом врача с пациентом-симулятором."""

    def __init__(self, patient: Patient, card: MedicalCard) -> None:
        self.patient = patient
        self.card = card
        self._stage = "greeting"
        self._history: list[dict[str, Any]] = []
        self._llm = GigachatResponseGenerator(
            disease_name=patient.disease.name,
            complaints=patient.disease.complaints,
        )
        logger.info("DialogEngine initialized for patient %s", patient.fio)

    def process(self, text: str) -> str:
        self._history.append({"role": "user", "content": text})

        if self._stage == "greeting":
            context = self._build_context(
                extra="Ты только что зашёл в кабинет врача. Это начало приёма."
            )
            self._stage = "dialog"
        else:
            context = self._build_context()

        response = self._llm.generate_response(
            context=context,
            dialog_messages=self._history[-20:],
        )
        self._history.append({"role": "assistant", "content": response})
        return response

    def reset(self) -> None:
        self._stage = "greeting"
        self._history.clear()
        logger.info("Dialog reset for patient %s", self.patient.fio)

    # ------------------------------------------------------------------ #

    def _build_context(self, extra: str = "") -> str:
        p, d = self.patient, self.patient.disease
        ctx = (
            f"Информация о моей болезни:\n"
            f"  - Диагноз (скрыт от врача): {d.name}\n"
            f"  - Основные симптомы: {', '.join(d.complaints)}\n"
            f"  - История развития: {', '.join(d.anamnesis)}\n"
            f"  - Проведённые обследования: {', '.join(d.diagnostics)}\n\n"
            f"Мой профиль:\n"
            f"  - Возраст: {p.age}\n"
            f"  - Профессия: {p.profession}\n"
            f"  - Пол: {p.gender}\n"
        )
        if self.card.complaints:
            ctx += f"\nУже сообщённые жалобы: {', '.join(self.card.complaints)}"
        if extra:
            ctx += f"\n\nДополнительно: {extra}"
        return ctx
