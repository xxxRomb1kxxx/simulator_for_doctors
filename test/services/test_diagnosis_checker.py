import pytest

from services.diagnosis_checker import check, similarity_score


class TestDiagnosisChecker:

    @pytest.mark.parametrize("user, correct, expected", [
        # Точные совпадения
        ("Острый аппендицит", "Острый аппендицит", True),
        ("Сахарный диабет 2 типа", "Сахарный диабет 2 типа", True),
        ("Железодефицитная анемия", "Железодефицитная анемия", True),
        ("Инфильтративный туберкулёз лёгких", "Инфильтративный туберкулёз лёгких", True),
        ("Идиопатическая генерализованная эпилепсия", "Идиопатическая генерализованная эпилепсия", True),
        # Регистр
        ("ОСТРЫЙ АППЕНДИЦИТ", "Острый аппендицит", True),
        ("сахарный диабет 2 типа", "Сахарный диабет 2 типа", True),
        # Опечатки
        ("Острый апендицит", "Острый аппендицит", True),
        # ё → е нормализация (ИСПРАВЛЕН баг оригинала)
        ("туберкулез", "туберкулёз", True),
        ("Туберкулез легких", "Туберкулёз лёгких", True),
        # Синонимы (краткие названия, НОВАЯ фича)
        ("аппендицит", "Острый аппендицит", True),
        ("диабет 2 типа", "Сахарный диабет 2 типа", True),
        ("анемия", "Железодефицитная анемия", True),
        ("эпилепсия", "Идиопатическая генерализованная эпилепсия", True),
        # Неверные
        ("Грипп", "Острый аппендицит", False),
        ("Гастрит", "Железодефицитная анемия", False),
        ("Бронхит", "Инфильтративный туберкулёз лёгких", False),
    ])
    def test_check(self, user: str, correct: str, expected: bool) -> None:
        assert check(user, correct) == expected, f"'{user}' vs '{correct}'"

    @pytest.mark.parametrize("user, correct", [
        ("", "Острый аппендицит"),
        ("Аппендицит", ""),
    ])
    def test_empty_string(self, user: str, correct: str) -> None:
        result = check(user, correct)
        assert isinstance(result, bool)
        assert result is False

    def test_both_empty(self) -> None:
        # SequenceMatcher("", "") == 1.0 → True
        assert check("", "") is True

    def test_none_raises(self) -> None:
        with pytest.raises((TypeError, AttributeError)):
            check(None, "диагноз")  # type: ignore

    def test_similarity_score_returns_float(self) -> None:
        score = similarity_score("Аппендицит", "Острый аппендицит")
        assert 0.0 <= score <= 1.0

    def test_similarity_score_perfect(self) -> None:
        assert similarity_score("Острый аппендицит", "Острый аппендицит") == 1.0
