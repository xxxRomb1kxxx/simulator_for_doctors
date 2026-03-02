import pytest

from models.entities.disease import Disease, DiseaseType
from models.entities.medical_card import MedicalCard
from models.entities.patient import Patient
from models.patient_factory import create_patient


@pytest.fixture
def sample_disease() -> Disease:
    return Disease(
        name="Грипп",
        complaints=["Высокая температура", "Кашель"],
        anamnesis=["Заболел 3 дня назад"],
        diagnostics=["Общий анализ крови"],
        correct_diagnosis="ОРВИ",
    )


@pytest.fixture
def sample_patient(sample_disease: Disease) -> Patient:
    return Patient(
        fio="Иванов Иван Иванович",
        gender="М",
        age=35,
        profession="Инженер",
        disease=sample_disease,
    )


@pytest.fixture
def empty_card() -> MedicalCard:
    return MedicalCard()


@pytest.fixture
def appendicitis_patient() -> Patient:
    return create_patient(DiseaseType.APPENDICITIS)


@pytest.fixture
def diabetes_patient() -> Patient:
    return create_patient(DiseaseType.DIABETES)
