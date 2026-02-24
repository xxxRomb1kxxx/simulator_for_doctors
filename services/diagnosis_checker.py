from difflib import SequenceMatcher
from typing import Optional

# Синонимы: ключ → правильный диагноз (или его часть)
# Позволяет принимать краткие варианты ("аппендицит" → "острый аппендицит")
_SYNONYMS: dict[str, str] = {
    "аппендицит": "острый аппендицит",
    "острый аппендицит": "острый аппендицит",
    "диабет": "сахарный диабет 2 типа",
    "сахарный диабет": "сахарный диабет 2 типа",
    "диабет 2 типа": "сахарный диабет 2 типа",
    "анемия": "железодефицитная анемия",
    "железодефицитная анемия": "железодефицитная анемия",
    "туберкулез": "инфильтративный туберкулез легких",
    "туберкулёз": "инфильтративный туберкулез легких",
    "туберкулез легких": "инфильтративный туберкулез легких",
    "эпилепсия": "идиопатическая генерализованная эпилепсия",
}

_THRESHOLD = 0.8


def _normalize(text: str) -> str:
    """Приводит к нижнему регистру и заменяет ё → е."""
    return text.lower().replace("ё", "е").strip()


def check(user_diag: str, correct: str) -> bool:
    """
    Возвращает True если диагноз пользователя достаточно близок к правильному.

    Args:
        user_diag: Диагноз, введённый пользователем.
        correct: Эталонный диагноз из базы болезней.

    Raises:
        TypeError: если любой аргумент не str (сохранено поведение оригинала).
    """
    user_norm = _normalize(user_diag)
    correct_norm = _normalize(correct)

    # Синоним пользователя → нормализованный эталон
    canonical_user = _SYNONYMS.get(user_norm, user_norm)
    # Синоним эталона (на случай если в базе "ё")
    canonical_correct = _SYNONYMS.get(correct_norm, correct_norm)

    similarity = SequenceMatcher(None, canonical_user, canonical_correct).ratio()
    return similarity >= _THRESHOLD


def similarity_score(user_diag: str, correct: str) -> float:
    """Возвращает числовой score схожести (для отладки / расширенного фидбека)."""
    user_norm = _SYNONYMS.get(_normalize(user_diag), _normalize(user_diag))
    correct_norm = _SYNONYMS.get(_normalize(correct), _normalize(correct))
    return SequenceMatcher(None, user_norm, correct_norm).ratio()
