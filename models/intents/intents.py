INTENTS = {
    "complaints": ["жалоб", "боль"],
    "anamnesis": ["начал", "давно"],
    "diagnostics": ["анализ", "исслед"],
    "diagnosis": ["диагноз"]
}

def detect_intent(text: str):
    text = text.lower()
    for intent, keys in INTENTS.items():
        if any(k in text for k in keys):
            return intent
    return None
