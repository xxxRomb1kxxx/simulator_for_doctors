class MedicalCard:
    def __init__(self):
        self.complaints = []
        self.anamnesis = []
        self.diagnostics = []
        self.diagnosis = None

    def render(self):
        return (
            "📋 Медицинская карта\n\n"
            f"Жалобы:\n- " + "\n- ".join(self.complaints) + "\n\n"
            f"Анамнез:\n- " + "\n- ".join(self.anamnesis) + "\n\n"
            f"Диагностика:\n- " + "\n- ".join(self.diagnostics) + "\n\n"
            f"Диагноз: {self.diagnosis}"
        )
