import logging
from typing import Any

from giga.llm_response_generator import GigachatResponseGenerator, GigachatCardParser, IResponseGenerator, ICardParser
from models.models import MedicalCard, Patient

logger = logging.getLogger(__name__)


class DialogEngine:
    """Управляет диалогом врача с пациентом-симулятором."""

    def __init__(
        self,
        patient: Patient,
        card: MedicalCard,
        llm: IResponseGenerator |None = None,
        card_parser: ICardParser |None = None,
    ) -> None:
        self.patient = patient
        self.card = card
        self._stage = "greeting"
        self._history: list[dict[str, Any]] = []
        self._llm: IResponseGenerator = llm or GigachatResponseGenerator(
            disease_name=patient.disease.name,
            complaints=patient.disease.complaints,
        )
        self._card_parser: ICardParser = card_parser or GigachatCardParser()
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
        self._update_card(doctor_question=text, patient_reply=response)
        return response

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

    def _update_card(self, doctor_question: str, patient_reply: str) -> None:
        try:
            data = self._card_parser.extract_medical_data(
                doctor_question=doctor_question,
                patient_reply=patient_reply,
            )
            self._merge_into_card(data)
        except Exception:
            logger.exception("Card update failed, skipping")

    def _merge_into_card(self, data: dict) -> None:
        existing_complaints  = {x.lower() for x in self.card.complaints}
        existing_anamnesis   = {x.lower() for x in self.card.anamnesis}
        existing_diagnostics = {x.lower() for x in self.card.diagnostics}

        for item in data.get("complaints", []):
            if item and item.lower() not in existing_complaints:
                self.card.complaints.append(item)
                existing_complaints.add(item.lower())

        for item in data.get("anamnesis", []):
            if item and item.lower() not in existing_anamnesis:
                self.card.anamnesis.append(item)
                existing_anamnesis.add(item.lower())

        for item in data.get("diagnostics", []):
            if item and item.lower() not in existing_diagnostics:
                self.card.diagnostics.append(item)
                existing_diagnostics.add(item.lower())