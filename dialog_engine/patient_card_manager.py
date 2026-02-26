from models.entities.medical_card import MedicalCard
from models.entities.patient import Patient


class PatientCardManager:

    def __init__(self, patient: Patient, card: MedicalCard) -> None:
        self.patient = patient
        self.card = card

    def get_disease_context(self) -> str:
        p = self.patient
        d = p.disease
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
        return ctx
