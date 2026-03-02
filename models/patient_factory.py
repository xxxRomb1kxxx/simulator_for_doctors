import random

from models.models import Disease, DiseaseType, Patient
from models.disease_registry import DISEASE_REGISTRY

DISEASE_DATA = {
    dt: {
        "name": cfg.name,
        "complaints": cfg.complaints,
        "anamnesis": cfg.anamnesis,
        "diagnostics": cfg.diagnostics,
        "correct_diagnosis": cfg.correct_diagnosis,
    }
    for dt, cfg in DISEASE_REGISTRY.items()
}
disease_data = DISEASE_DATA

_AGE_RANGES: dict[DiseaseType, tuple[int, int]] = {
    DiseaseType.APPENDICITIS: (18, 40),
    DiseaseType.DIABETES:     (45, 65),
    DiseaseType.ANEMIA:       (25, 60),
    DiseaseType.TUBERCULOSIS: (25, 50),
    DiseaseType.EPILEPSY:     (20, 35),
}

_MALE_PATIENTS = [
    ("Иванов Иван Иванович", "М"),
    ("Петров Сергей Александрович", "М"),
    ("Сидоров Андрей Николаевич", "М"),
    ("Козлов Дмитрий Викторович", "М"),
    ("Новиков Алексей Павлович", "М"),
]
_FEMALE_PATIENTS = [
    ("Смирнова Анна Сергеевна", "Ж"),
    ("Кузнецова Елена Ивановна", "Ж"),
    ("Попова Наталья Андреевна", "Ж"),
    ("Соколова Мария Дмитриевна", "Ж"),
    ("Волкова Ольга Владимировна", "Ж"),
]
_ALL_PATIENTS = _MALE_PATIENTS + _FEMALE_PATIENTS

_PROFESSIONS = [
    "Рабочий", "Офисный сотрудник", "Учитель",
    "Водитель", "Продавец", "Инженер", "Бухгалтер",
]


def create_patient(disease_type: DiseaseType) -> Patient:
    if disease_type not in DISEASE_REGISTRY:
        raise ValueError(f"Unknown disease type: {disease_type!r}")

    cfg = DISEASE_REGISTRY[disease_type]
    disease = Disease(
        name=cfg.name,
        complaints=list(cfg.complaints),
        anamnesis=list(cfg.anamnesis),
        diagnostics=list(cfg.diagnostics),
        correct_diagnosis=cfg.correct_diagnosis,
    )

    age_min, age_max = _AGE_RANGES[disease_type]
    fio, gender = random.choice(_ALL_PATIENTS)

    return Patient(
        fio=fio,
        gender=gender,  # type: ignore[arg-type]
        age=random.randint(age_min, age_max),
        profession=random.choice(_PROFESSIONS),
        disease=disease,
    )