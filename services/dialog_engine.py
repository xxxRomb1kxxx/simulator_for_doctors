from models.intents.intents import detect_intent

class DialogEngine:
    def __init__(self, patient, card):
        self.patient = patient
        self.card = card
        self.stage = "greeting"  # 👈 ВАЖНО

    def process(self, text: str) -> str:
        text = text.lower()

        if self.stage == "greeting":
            if any(w in text for w in ["проход", "сад", "да"]):
                self.stage = "dialog"
                return "Спасибо, доктор."

            return "Можно войти?"

        intent = detect_intent(text)

        if not intent:
            return "Я не понимаю, что вы хотите уточнить."

        if intent == "complaints":
            self.card.complaints = self.patient.disease.complaints
            return ", ".join(self.card.complaints)

        if intent == "anamnesis":
            self.card.anamnesis = self.patient.disease.anamnesis
            return ", ".join(self.card.anamnesis)

        if intent == "diagnostics":
            self.card.diagnostics = self.patient.disease.diagnostics
            return ", ".join(self.card.diagnostics)

        if intent == "diagnosis":
            return "Какой у меня диагноз?"

        return ""
