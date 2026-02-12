import pytest
from services.patient_factory import create_patient, disease_data
from models.entities.disease import DiseaseType
from models.entities.patient import Patient


class TestPatientFactory:

    def test_create_patient_appendicitis(self):
        patient = create_patient(DiseaseType.APPENDICITIS)

        assert isinstance(patient, Patient)
        assert patient.fio == "Иванов Иван Иванович"
        assert patient.gender == "М"
        assert isinstance(patient.age, int)
        assert 18 <= patient.age <= 40
        assert patient.profession in ["Рабочий", "Офисный сотрудник", "Учитель", "Водитель", "Продавец"]
        assert patient.disease.name == "Аппендицит"
        assert patient.disease.correct_diagnosis == "Острый аппендицит"
        assert len(patient.disease.complaints) > 0
        assert len(patient.disease.anamnesis) > 0
        assert len(patient.disease.diagnostics) > 0

    def test_create_patient_diabetes(self):
        patient = create_patient(DiseaseType.DIABETES)

        assert isinstance(patient, Patient)
        assert 45 <= patient.age <= 65
        assert patient.disease.name == "Сахарный диабет"
        assert patient.disease.correct_diagnosis == "Сахарный диабет 2 типа"

    def test_create_patient_anemia(self):
        patient = create_patient(DiseaseType.ANEMIA)

        assert isinstance(patient, Patient)
        assert 25 <= patient.age <= 60
        assert patient.disease.name == "Анемия"
        assert patient.disease.correct_diagnosis == "Железодефицитная анемия"

    def test_create_patient_tuberculosis(self):
        patient = create_patient(DiseaseType.TUBERCULOSIS)

        assert isinstance(patient, Patient)
        assert 25 <= patient.age <= 50
        assert patient.disease.name == "Туберкулёз"
        assert patient.disease.correct_diagnosis == "Инфильтративный туберкулёз лёгких"

    def test_create_patient_epilepsy(self):
        patient = create_patient(DiseaseType.EPILEPSY)

        assert isinstance(patient, Patient)
        assert 20 <= patient.age <= 35
        assert patient.disease.name == "Эпилепсия"
        assert patient.disease.correct_diagnosis == "Идиопатическая генерализованная эпилепсия"

    def test_create_patient_invalid_disease_type(self):
        with pytest.raises(ValueError, match="Unknown disease type"):
            create_patient("invalid_type")

    def test_all_disease_types_have_data(self):
        for disease_type in DiseaseType:
            assert disease_type in disease_data
            data = disease_data[disease_type]

            assert "name" in data
            assert "complaints" in data
            assert "anamnesis" in data
            assert "diagnostics" in data
            assert "correct_diagnosis" in data

            assert isinstance(data["name"], str)
            assert isinstance(data["complaints"], list)
            assert isinstance(data["anamnesis"], list)
            assert isinstance(data["diagnostics"], list)
            assert isinstance(data["correct_diagnosis"], str)