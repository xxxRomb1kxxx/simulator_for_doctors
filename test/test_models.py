from models.entities.patient import Patient
from models.entities.disease import Disease
from models.entities.medical_card import MedicalCard


def test_patient_creation():
    patient = Patient(name="Иван", age=30, gender="M")

    assert patient.name == "Иван"
    assert patient.age == 30
    assert patient.gender == "M"


def test_disease_is_immutable():
    disease = Disease(name="Грипп", symptoms=["температура", "кашель"])

    assert "кашель" in disease.symptoms


def test_medical_card_add_note():
    card = MedicalCard()
    card.add_note("Пациент жалуется на боль")

    assert len(card.notes) == 1
