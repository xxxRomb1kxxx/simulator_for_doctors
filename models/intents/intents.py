INTENTS = {
    "complaints": ["жалоб", "боль", "беспокоит", "симптом", "болит"],
    "anamnesis": ["начал", "давно", "началось", "появил", "возник"],
    "diagnostics": ["анализ", "исслед", "обслед", "тест", "узи", "рентген"],
    "diagnosis": ["диагноз", "заболеван", "болезнь", "что у меня"]
}

def detect_intent(text: str):
    text = text.lower()
    for intent, keys in INTENTS.items():
        if any(k in text for k in keys):
            return intent
    return None