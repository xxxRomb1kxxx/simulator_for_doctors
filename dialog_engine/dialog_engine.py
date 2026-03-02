import logging
from typing import Any

from giga.llm_response_generator import GigachatResponseGenerator, IResponseGenerator
from models.models import MedicalCard, Patient

logger = logging.getLogger(__name__)


class DialogEngine:
    """Управляет диалогом врача с пациентом-симулятором."""

    def __init__(
        self,
        patient: Patient,
        card: MedicalCard,
        llm: IResponseGenerator | None = None,
    ) -> None:
        self.patient = patient
        self.card = card
        self._stage = "greeting"
        self._history: list[dict[str, Any]] = []
        self._llm: IResponseGenerator = llm or GigachatResponseGenerator(
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

        result = self._llm.generate(
            context=context,
            dialog_messages=self._history[-20:],
        )

        self._history.append({"role": "assistant", "content": result.text})
        self._merge_into_card(result)
        return result.text

    def reset(self) -> None:
        self._stage = "greeting"
        self._history.clear()
        logger.info("Dialog reset for patient %s", self.patient.fio)

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

    def _merge_into_card(self, result) -> None:
        existing_complaints  = {x.lower() for x in self.card.complaints}
        existing_anamnesis   = {x.lower() for x in self.card.anamnesis}
        existing_diagnostics = {x.lower() for x in self.card.diagnostics}

        for item in result.complaints:
            if item and item.lower() not in existing_complaints:
                self.card.complaints.append(item)
                existing_complaints.add(item.lower())

        for item in result.anamnesis:
            if item and item.lower() not in existing_anamnesis:
                self.card.anamnesis.append(item)
                existing_anamnesis.add(item.lower())

        for item in result.diagnostics:
            if item and item.lower() not in existing_diagnostics:
                self.card.diagnostics.append(item)
                existing_diagnostics.add(item.lower())