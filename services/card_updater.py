import logging
from typing import List

from models.models import MedicalCard

logger = logging.getLogger(__name__)

_COMPLAINT_KEYWORDS = [
    "болит", "боль", "жжение", "тошнота", "рвота", "температура",
    "слабость", "головокружение", "кашель", "одышка", "жажда",
    "потею", "потливость", "обморок", "судороги", "усталость",
    "зуд", "отёк", "отек", "давление", "колет", "ломит",
]

_ANAMNESIS_KEYWORDS = [
    "давно", "неделю", "месяц", "год", "началось", "раньше",
    "до этого", "хронич", "в детстве", "операция", "травма",
    "несколько дней", "уже", "всегда", "периодически",
]

_DIAGNOSTIC_KEYWORDS = [
    "анализ", "узи", "рентген", "мрт", "кт", "экг",
    "флюорография", "кровь", "обследование", "снимок", "сдавал",
]


def _deduplicate(existing: List[str], new_items: List[str]) -> List[str]:
    """Добавляет только те элементы, которых ещё нет (без учёта регистра)."""
    lowered = {x.lower() for x in existing}
    result = list(existing)
    for item in new_items:
        if item.strip() and item.lower() not in lowered:
            result.append(item)
            lowered.add(item.lower())
    return result


def update_card_from_patient_reply(
    card: MedicalCard,
    patient_reply: str,
    doctor_question: str = "",
) -> None:
    """
    Обновляет медицинскую карту на основе ответа пациента.

    Использует эвристику по ключевым словам.
    Для production рекомендуется заменить на LLM-вызов в JSON mode.
    """
    try:
        _heuristic_update(card, patient_reply, doctor_question)
    except Exception:
        logger.exception("Card update failed, skipping")


def _heuristic_update(
    card: MedicalCard,
    reply: str,
    question: str,
) -> None:
    sentences = [
        s.strip()
        for s in reply.replace("!", ".").replace("?", ".").split(".")
        if s.strip()
    ]

    new_complaints: List[str] = []
    new_anamnesis: List[str] = []
    new_diagnostics: List[str] = []

    for sentence in sentences:
        low = sentence.lower()
        is_complaint   = any(kw in low for kw in _COMPLAINT_KEYWORDS)
        is_anamnesis   = any(kw in low for kw in _ANAMNESIS_KEYWORDS)
        is_diagnostic  = any(kw in low for kw in _DIAGNOSTIC_KEYWORDS)

        # Приоритет: диагностика > анамнез > жалоба
        if is_diagnostic:
            new_diagnostics.append(sentence)
        elif is_anamnesis and not is_complaint:
            new_anamnesis.append(sentence)
        elif is_complaint:
            new_complaints.append(sentence)

    # Если врач спрашивает про историю — смещаем жалобы в анамнез
    question_low = question.lower()
    if any(kw in question_low for kw in ["когда", "давно", "началось", "история", "раньше"]):
        new_anamnesis.extend(new_complaints)
        new_complaints = []

    card.complaints  = _deduplicate(card.complaints,  new_complaints)
    card.anamnesis   = _deduplicate(card.anamnesis,   new_anamnesis)
    card.diagnostics = _deduplicate(card.diagnostics, new_diagnostics)

    logger.debug(
        "Card updated: +%d complaints, +%d anamnesis, +%d diagnostics",
        len(new_complaints), len(new_anamnesis), len(new_diagnostics),
    )