from difflib import SequenceMatcher

from models.patient_factory import DISEASE_DATA


# Ключ — нормализованный краткий вариант, значение — нормализованный полный диагноз.
def _build_synonyms() -> dict[str, str]:
    short: dict[str, str] = {
        "аппендицит": "острый аппендицит",
        "диабет": "сахарный диабет 2 типа",
        "диабет 2 типа": "сахарный диабет 2 типа",
        "анемия": "железодефицитная анемия",
        "туберкулез": "инфильтративный туберкулез легких",
        "туберкулёз": "инфильтративный туберкулез легких",
        "туберкулез легких": "инфильтративный туберкулез легких",
        "эпилепсия": "идиопатическая генерализованная эпилепсия",
    }
    # Добавляем все правильные диагнозы как синонимы самих себя (с нормализацией ё → е)
    for data in DISEASE_DATA.values():
        norm = _normalize(data["correct_diagnosis"])
        short[norm] = norm
    return short


def _normalize(text: str) -> str:
    return text.lower().replace("ё", "е").strip()


_SYNONYMS: dict[str, str] = _build_synonyms()
_THRESHOLD = 0.8


def check(user_diag: str, correct: str) -> bool:
    """Возвращает True, если диагноз пользователя достаточно близок к правильному."""
    user_norm = _normalize(user_diag)
    correct_norm = _normalize(correct)

    canonical_user = _SYNONYMS.get(user_norm, user_norm)
    canonical_correct = _SYNONYMS.get(correct_norm, correct_norm)

    return SequenceMatcher(None, canonical_user, canonical_correct).ratio() >= _THRESHOLD


def similarity_score(user_diag: str, correct: str) -> float:
    """Числовой score схожести для расширенного фидбека."""
    user_norm = _SYNONYMS.get(_normalize(user_diag), _normalize(user_diag))
    correct_norm = _SYNONYMS.get(_normalize(correct), _normalize(correct))
    return SequenceMatcher(None, user_norm, correct_norm).ratio()
