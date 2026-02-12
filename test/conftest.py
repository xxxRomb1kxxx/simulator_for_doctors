import pytest
from models.entities.disease import Disease, DiseaseType
from models.entities.patient import Patient
from services.patient_factory import create_patient

@pytest.fixture
def sample_disease():
    return Disease(
        name="Грипп",
        complaints=["Высокая температура", "Кашель", "Слабость"],
        anamnesis=["Заболел 3 дня назад", "Температура 38.5"],
        diagnostics=["Общий анализ крови", "Мазок из зева"],
        correct_diagnosis="ОРВИ"
    )

@pytest.fixture
def sample_patient(sample_disease):
    return Patient(
        fio="Иванов Иван Иванович",
        gender="М",
        age=35,
        profession="Инженер",
        disease=sample_disease
    )

@pytest.fixture
def appendicitis_patient():

    return create_patient(DiseaseType.APPENDICITIS)

@pytest.fixture
def diabetes_patient():
    return create_patient(DiseaseType.DIABETES)

@pytest.fixture
def anemia_patient():
    return create_patient(DiseaseType.ANEMIA)

@pytest.fixture
def tuberculosis_patient():
    return create_patient(DiseaseType.TUBERCULOSIS)

@pytest.fixture
def epilepsy_patient():
    return create_patient(DiseaseType.EPILEPSY)