import random
from typing import TypedDict

from models.entities.disease import Disease, DiseaseType
from models.entities.patient import Patient

class DiseaseData(TypedDict):
    name: str
    complaints: list[str]
    anamnesis: list[str]
    diagnostics: list[str]
    correct_diagnosis: str


DISEASE_DATA: dict[DiseaseType, DiseaseData] = {
    DiseaseType.APPENDICITIS: {
        "name": "Аппендицит",
        "complaints": [
            "Острая боль в правой нижней части живота",
            "Тошнота",
            "Потеря аппетита",
        ],
        "anamnesis": [
            "Симптомы начались около 6 часов назад",
            "Сначала была боль вокруг пупка",
            "Боль переместилась вправо вниз",
        ],
        "diagnostics": [
            "Лейкоцитоз в анализе крови",
            "Положительный симптом Щёткина-Блюмберга",
            "УЗИ показало утолщение аппендикса",
        ],
        "correct_diagnosis": "Острый аппендицит",
    },
    DiseaseType.DIABETES: {
        "name": "Сахарный диабет",
        "complaints": [
            "Сильная постоянная жажда",
            "Частое мочеиспускание",
            "Слабость",
            "Сухость во рту",
        ],
        "anamnesis": [
            "Симптомы нарастали постепенно в течение 3–4 месяцев",
            "Заметил, что стал много пить",
        ],
        "diagnostics": [
            "Глюкоза крови натощак 12.8 ммоль/л",
            "Гликированный гемоглобин 9.2%",
        ],
        "correct_diagnosis": "Сахарный диабет 2 типа",
    },
    DiseaseType.ANEMIA: {
        "name": "Анемия",
        "complaints": [
            "Постоянная слабость",
            "Головокружение",
            "Одышка при физической нагрузке",
            "Бледность кожи",
        ],
        "anamnesis": [
            "Состояние ухудшалось постепенно в течение нескольких месяцев",
            "Стал замечать, что быстро устаю",
        ],
        "diagnostics": [
            "Гемоглобин 85 г/л",
            "Снижен уровень сывороточного железа",
            "Цветовой показатель 0.7",
        ],
        "correct_diagnosis": "Железодефицитная анемия",
    },
    DiseaseType.TUBERCULOSIS: {
        "name": "Туберкулёз",
        "complaints": [
            "Кашель более 3 недель",
            "Потеря веса на 4 кг за месяц",
            "Ночная потливость",
            "Субфебрильная температура",
        ],
        "anamnesis": [
            "Кашель начался около месяца назад",
            "Сначала был сухим, теперь с мокротой",
        ],
        "diagnostics": [
            "На рентгене инфильтративные изменения в верхней доле правого лёгкого",
            "Мокрота на БК положительная",
        ],
        "correct_diagnosis": "Инфильтративный туберкулёз лёгких",
    },
    DiseaseType.EPILEPSY: {
        "name": "Эпилепсия",
        "complaints": [
            "Периодические судорожные приступы",
            "Потеря сознания во время приступов",
            "Чувство страха перед приступом",
        ],
        "anamnesis": [
            "Первый приступ был год назад",
            "С тех пор приступы повторялись 2–3 раза",
        ],
        "diagnostics": [
            "На ЭЭГ регистрируются эпилептические разряды",
            "МРТ без структурных изменений",
        ],
        "correct_diagnosis": "Идиопатическая генерализованная эпилепсия",
    },
}

# --- Возрастные диапазоны ---
_AGE_RANGES: dict[DiseaseType, tuple[int, int]] = {
    DiseaseType.APPENDICITIS: (18, 40),
    DiseaseType.DIABETES: (45, 65),
    DiseaseType.ANEMIA: (25, 60),
    DiseaseType.TUBERCULOSIS: (25, 50),
    DiseaseType.EPILEPSY: (20, 35),
}

# --- Пул пациентов (имена + пол) ---
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
    if disease_type not in DISEASE_DATA:
        raise ValueError(f"Unknown disease type: {disease_type!r}")

    data = DISEASE_DATA[disease_type]
    disease = Disease(
        name=data["name"],
        complaints=data["complaints"],
        anamnesis=data["anamnesis"],
        diagnostics=data["diagnostics"],
        correct_diagnosis=data["correct_diagnosis"],
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


# Публичный алиас для обратной совместимости тестов
disease_data = DISEASE_DATA
