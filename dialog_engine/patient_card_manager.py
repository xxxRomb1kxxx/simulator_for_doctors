from models.entities.patient import Patient


class PatientCardManager:
    """Класс для управления медицинской картой пациента"""

    def __init__(self, patient: Patient, card):
        self.patient = patient
        self.card = card

    def update_complaints(self, complaints: list):
        """Обновить жалобы в карте"""
        self.card.complaints = complaints

    def update_anamnesis(self, anamnesis: list):
        """Обновить анамнез в карте"""
        self.card.anamnesis = anamnesis

    def update_diagnostics(self, diagnostics: list):
        """Обновить диагностику в карте"""
        self.card.diagnostics = diagnostics

    def get_disease_context(self) -> str:
        """Получить контекст болезни в текстовом формате"""
        return f"""
        Информация о моей болезни:
        - Диагноз: {self.patient.disease.name}
        - Основные симптомы: {', '.join(self.patient.disease.complaints)}
        - История развития: {', '.join(self.patient.disease.anamnesis)}
        - Проведённые обследования: {', '.join(self.patient.disease.diagnostics)}

        Мой профиль:
        - Возраст: {self.patient.age}
        - Профессия: {self.patient.profession}
        - Пол: {self.patient.gender}
        """