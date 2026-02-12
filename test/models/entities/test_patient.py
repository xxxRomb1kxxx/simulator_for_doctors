import pytest
from models.entities.patient import Patient
from models.entities.disease import Disease
def test_patient_creation():
    disease = Disease(
        name="Грипп",
        complaints=["Температура", "Кашель"],
        anamnesis=["Болеет 2 дня"],
        diagnostics=["Общий анализ крови"],
        correct_diagnosis="ОРВИ"
    )

    patient = Patient(
        fio="Иванов Иван Иванович",
        gender="М",
        age=30,
        profession="Врач",
        disease=disease
    )

    assert patient.fio == "Иванов Иван Иванович"
    assert patient.gender == "М"
    assert patient.age == 30
    assert patient.profession == "Врач"
    assert patient.disease == disease
    assert patient.disease.name == "Грипп"


def test_patient_gender_literal():
    """Тест, что gender принимает только допустимые значения."""
    disease = Disease(
        name="Тест",
        complaints=[],
        anamnesis=[],
        diagnostics=[],
        correct_diagnosis=""
    )

    patient_m = Patient("Тест", "М", 20, "Инженер", disease)
    patient_f = Patient("Тест", "Ж", 20, "Инженер", disease)

    assert patient_m.gender == "М"
    assert patient_f.gender == "Ж"


    patient_x = Patient("Тест", "X", 20, "Инженер", disease)
    assert patient_x.gender == "X"