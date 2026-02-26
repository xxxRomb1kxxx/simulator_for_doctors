import pytest

from models.entities.disease import DiseaseType
from models.entities.patient import Patient
from models.patient_factory import DISEASE_DATA, create_patient

_ALL_FIOS = {
    "Иванов Иван Иванович", "Петров Сергей Александрович",
    "Сидоров Андрей Николаевич", "Козлов Дмитрий Викторович",
    "Новиков Алексей Павлович", "Смирнова Анна Сергеевна",
    "Кузнецова Елена Ивановна", "Попова Наталья Андреевна",
    "Соколова Мария Дмитриевна", "Волкова Ольга Владимировна",
}


class TestPatientFactory:

    @pytest.mark.parametrize("disease_type,age_min,age_max,disease_name,correct_diagnosis", [
        (DiseaseType.APPENDICITIS, 18, 40, "Аппендицит", "Острый аппендицит"),
        (DiseaseType.DIABETES, 45, 65, "Сахарный диабет", "Сахарный диабет 2 типа"),
        (DiseaseType.ANEMIA, 25, 60, "Анемия", "Железодефицитная анемия"),
        (DiseaseType.TUBERCULOSIS, 25, 50, "Туберкулёз", "Инфильтративный туберкулёз лёгких"),
        (DiseaseType.EPILEPSY, 20, 35, "Эпилепсия", "Идиопатическая генерализованная эпилепсия"),
    ])
    def test_create_patient(
        self, disease_type, age_min, age_max, disease_name, correct_diagnosis
    ) -> None:
        patient = create_patient(disease_type)
        assert isinstance(patient, Patient)
        assert patient.fio in _ALL_FIOS
        assert patient.gender in ("М", "Ж")
        assert age_min <= patient.age <= age_max
        assert patient.disease.name == disease_name
        assert patient.disease.correct_diagnosis == correct_diagnosis
        assert len(patient.disease.complaints) > 0
        assert len(patient.disease.anamnesis) > 0
        assert len(patient.disease.diagnostics) > 0

    def test_invalid_disease_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown disease type"):
            create_patient("invalid")  # type: ignore

    def test_all_disease_types_have_data(self) -> None:
        for dt in DiseaseType:
            assert dt in DISEASE_DATA
            data = DISEASE_DATA[dt]
            assert all(k in data for k in ("name", "complaints", "anamnesis", "diagnostics", "correct_diagnosis"))

    def test_randomized_names(self) -> None:
        """Проверяем, что имена действительно рандомизируются (не всегда Иванов)."""
        names = {create_patient(DiseaseType.APPENDICITIS).fio for _ in range(30)}
        assert len(names) > 1, "Имена должны быть рандомными"
