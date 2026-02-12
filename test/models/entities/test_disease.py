import pytest
from models.entities.disease import Disease, DiseaseType


def test_disease_creation():
    disease = Disease(
        name="Аппендицит",
        complaints=["Боль в животе", "Тошнота"],
        anamnesis=["Боль началась 6 часов назад"],
        diagnostics=["УЗИ", "Анализ крови"],
        correct_diagnosis="Острый аппендицит"
    )

    assert disease.name == "Аппендицит"
    assert len(disease.complaints) == 2
    assert len(disease.anamnesis) == 1
    assert len(disease.diagnostics) == 2
    assert disease.correct_diagnosis == "Острый аппендицит"


def test_disease_with_empty_lists():
    disease = Disease(
        name="Тестовое заболевание",
        complaints=[],
        anamnesis=[],
        diagnostics=[],
        correct_diagnosis=""
    )

    assert disease.name == "Тестовое заболевание"
    assert disease.complaints == []
    assert disease.anamnesis == []
    assert disease.diagnostics == []
    assert disease.correct_diagnosis == ""


def test_disease_is_mutable():
    disease = Disease(
        name="Грипп",
        complaints=["Температура"],
        anamnesis=["Болеет 2 дня"],
        diagnostics=["Анализ"],
        correct_diagnosis="ОРВИ"
    )

    disease.name = "ОРВИ"
    disease.complaints.append("Кашель")

    assert disease.name == "ОРВИ"
    assert len(disease.complaints) == 2


def test_disease_type_enum():
    assert len(DiseaseType) == 5
    assert DiseaseType.APPENDICITIS.value == "appendicitis"
    assert DiseaseType.DIABETES.value == "diabetes"
    assert DiseaseType.ANEMIA.value == "anemia"
    assert DiseaseType.TUBERCULOSIS.value == "tuberculosis"
    assert DiseaseType.EPILEPSY.value == "epilepsy"