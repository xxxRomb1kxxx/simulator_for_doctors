import pytest
from models.intents.intents import INTENTS, detect_intent


class TestIntents:

    def test_intents_structure(self):
        assert isinstance(INTENTS, dict)
        assert len(INTENTS) == 4

        expected_intents = ["complaints", "anamnesis", "diagnostics", "diagnosis"]
        for intent in expected_intents:
            assert intent in INTENTS
            assert isinstance(INTENTS[intent], list)
            assert len(INTENTS[intent]) > 0

    @pytest.mark.parametrize("text,expected_intent", [
        ("У меня болит голова", "complaints"),
        ("Жалуюсь на боль в животе", "complaints"),
        ("Беспокоит кашель", "complaints"),
        ("Симптомы: температура", "complaints"),

        ("Когда началось?", "anamnesis"),
        ("Как давно это появилось?", "anamnesis"),
        ("С чего началось?", "anamnesis"),
        ("Когда возникли симптомы?", "anamnesis"),

        ("Нужно сделать анализ крови", "diagnostics"),
        ("Какие исследования провести?", "diagnostics"),
        ("Назначьте обследование", "diagnostics"),
        ("Сделать УЗИ", "diagnostics"),
        ("Рентген показал", "diagnostics"),

        ("Какой диагноз?", "diagnosis"),
        ("Определите заболевание", "diagnosis"),
        ("Что за болезнь?", "diagnosis"),
        ("Что у меня?", "diagnosis"),

        ("Привет, как дела?", None),
        ("Спасибо, доктор", None),
        ("", None),
    ])
    def test_detect_intent(self, text, expected_intent):
        result = detect_intent(text)
        assert result == expected_intent

    def test_detect_intent_case_insensitive(self):
        result1 = detect_intent("БОЛИТ ЖИВОТ")
        result2 = detect_intent("болит живот")

        assert result1 == result2 == "complaints"

    def test_detect_intent_multiple_keywords(self):
        result = detect_intent("Болит живот, когда это началось?")
        assert result in ["complaints", "anamnesis"]

    def test_detect_intent_partial_match(self):
        assert detect_intent("жалоба") == "complaints"
        assert detect_intent("начало") == "anamnesis"
        assert detect_intent("анализ") == "diagnostics"
        assert detect_intent("диагноз") == "diagnosis"