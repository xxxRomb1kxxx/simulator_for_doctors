import pytest
from services.diagnosis_checker import check
from services.patient_factory import disease_data
from models.entities.disease import DiseaseType


class TestDiagnosisChecker:

    @pytest.mark.parametrize("user_diagnosis,correct_diagnosis,expected", [
        ("Острый аппендицит", "Острый аппендицит", True),
        ("Сахарный диабет 2 типа", "Сахарный диабет 2 типа", True),
        ("Железодефицитная анемия", "Железодефицитная анемия", True),
        ("Инфильтративный туберкулёз лёгких", "Инфильтративный туберкулёз лёгких", True),
        ("Идиопатическая генерализованная эпилепсия", "Идиопатическая генерализованная эпилепсия", True),

        ("Острый апендицит", "Острый аппендицит", True),
        ("Сахарный диабет 2го типа", "Сахарный диабет 2 типа", True),
        ("Железо-дефицитная анемия", "Железодефицитная анемия", True),

        ("ОСТРЫЙ АППЕНДИЦИТ", "Острый аппендицит", True),
        ("сахарный диабет 2 типа", "Сахарный диабет 2 типа", True),

        ("Туберкулез легких", "Инфильтративный туберкулёз лёгких", False),
        ("Эпилепсия", "Идиопатическая генерализованная эпилепсия", False),
    ])
    def test_correct_diagnoses(self, user_diagnosis, correct_diagnosis, expected):
        result = check(user_diagnosis, correct_diagnosis)
        assert result == expected, f"'{user_diagnosis}' vs '{correct_diagnosis}' -> {result}, expected {expected}"

    @pytest.mark.parametrize("user_diagnosis,correct_diagnosis", [
        ("Грипп", "Острый аппендицит"),
        ("ОРВИ", "Сахарный диабет 2 типа"),
        ("Гастрит", "Железодефицитная анемия"),
        ("Бронхит", "Инфильтративный туберкулёз лёгких"),
        ("Мигрень", "Идиопатическая генерализованная эпилепсия"),
        ("Аппендицит", "Сахарный диабет"),
        ("Кашель", "Туберкулёз"),
    ])
    def test_incorrect_diagnoses(self, user_diagnosis, correct_diagnosis):
        assert check(user_diagnosis, correct_diagnosis) is False

    @pytest.mark.parametrize("user_diagnosis,correct_diagnosis", [
        ("", "Острый аппендицит"),
        ("Аппендицит", ""),
        ("", ""),
    ])
    def test_edge_cases(self, user_diagnosis, correct_diagnosis):
        result = check(user_diagnosis, correct_diagnosis)
        assert isinstance(result, bool)
        if user_diagnosis == "" and correct_diagnosis == "":
            assert result is True
        else:
            assert result is False

    def test_edge_cases_with_none(self):
        with pytest.raises((TypeError, AttributeError)):
            check(None, "Диагноз")

        with pytest.raises((TypeError, AttributeError)):
            check("Диагноз", None)

        with pytest.raises((TypeError, AttributeError)):
            check(None, None)

    def test_similarity_threshold(self):
        assert check("Апендицит", "Аппендицит") is True  # Одна буква пропущена
        assert check("Аппендицит", "Апендицит") is True  # Симметрично

        assert check("Диабет", "Сахарный диабет") is False  # Слишком короткое
        assert check("Анемия", "Железодефицитная анемия") is False  # Слишком короткое
        assert check("Туберкулез", "Инфильтративный туберкулёз лёгких") is False  # Слишком короткое
        assert check("Эпилепсия", "Идиопатическая генерализованная эпилепсия") is False  # Слишком короткое

    def test_real_patient_scenarios(self, appendicitis_patient, diabetes_patient):
        assert check(
            appendicitis_patient.disease.correct_diagnosis,
            appendicitis_patient.disease.correct_diagnosis
        ) is True

        assert check(
            diabetes_patient.disease.correct_diagnosis,
            diabetes_patient.disease.correct_diagnosis
        ) is True

        assert check(
            "Грипп",
            appendicitis_patient.disease.correct_diagnosis
        ) is False

        assert check(
            "Аппендицит",
            appendicitis_patient.disease.correct_diagnosis
        ) is False

    def test_unicode_handling(self):
        assert check("туберкулез", "туберкулёз") is True
        assert check("Туберкулез легких", "Туберкулёз лёгких") is True

    def test_disease_data_diagnoses_variations(self):
        for disease_type in DiseaseType:
            correct = disease_data[disease_type]["correct_diagnosis"]

            assert check(correct, correct) is True

            short_name = correct.split()[0]
            if short_name:
                result = check(short_name, correct)
                print(f"{short_name} vs {correct}: {result}")

        assert check("Аппендицит", "Острый аппендицит") is False
        assert check("Диабет", "Сахарный диабет 2 типа") is False
        assert check("Анемия", "Железодефицитная анемия") is False
        assert check("Туберкулез", "Инфильтративный туберкулёз лёгких") is False
        assert check("Эпилепсия", "Идиопатическая генерализованная эпилепсия") is False