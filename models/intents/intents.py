from typing import Optional

INTENTS: dict[str, list[str]] = {
    "complaints": ["жалоб", "боль", "беспокоит", "симптом", "болит"],
    "anamnesis": ["начал", "давно", "началось", "появил", "возник"],
    "diagnostics": ["анализ", "исслед", "обслед", "тест", "узи", "рентген"],
    "diagnosis": ["диагноз", "заболеван", "болезнь", "что у меня"],
}


def detect_intent(text: str) -> Optional[str]:
    """Определяет intent по тексту. Возвращает None если ничего не найдено."""
    normalized = text.lower()
    for intent, keywords in INTENTS.items():
        if any(k in normalized for k in keywords):
            return intent
    return None
