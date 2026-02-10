from models.entities.patient import Patient
from models.entities.disease import Disease
from models.entities.disease import DiseaseType
import random

disease_data = {
        DiseaseType.APPENDICITIS: {
            "name": "Аппендицит",
            "complaints": ["Острая боль в правой нижней части живота", "Тошнота", "Потеря аппетита"],
            "anamnesis": ["Симптомы начались около 6 часов назад", "Сначала была боль вокруг пупка",
                          "Боль переместилась вправо вниз"],
            "diagnostics": ["Лейкоцитоз в анализе крови", "Положительный симптом Щёткина-Блюмберга",
                            "УЗИ показало утолщение аппендикса"],
            "correct_diagnosis": "Острый аппендицит"
        },
        DiseaseType.DIABETES: {
            "name": "Сахарный диабет",
            "complaints": ["Сильная постоянная жажда", "Частое мочеиспускание", "Слабость", "Сухость во рту"],
            "anamnesis": ["Симптомы нарастали постепенно в течение 3-4 месяцев", "Заметил, что стал много пить"],
            "diagnostics": ["Глюкоза крови натощак 12.8 ммоль/л", "Гликированный гемоглобин 9.2%"],
            "correct_diagnosis": "Сахарный диабет 2 типа"
        },
        DiseaseType.ANEMIA: {
            "name": "Анемия",
            "complaints": ["Постоянная слабость", "Головокружение", "Одышка при физической нагрузке", "Бледность кожи"],
            "anamnesis": ["Состояние ухудшалось постепенно в течение нескольких месяцев",
                          "Стал замечать, что быстро устаю"],
            "diagnostics": ["Гемоглобин 85 г/л", "Снижен уровень сывороточного железа", "Цветовой показатель 0.7"],
            "correct_diagnosis": "Железодефицитная анемия"
        },
        DiseaseType.TUBERCULOSIS: {
            "name": "Туберкулёз",
            "complaints": ["Кашель более 3 недель", "Потеря веса на 4 кг за месяц", "Ночная потливость",
                           "Субфебрильная температура"],
            "anamnesis": ["Кашель начался около месяца назад", "Сначала был сухим, теперь с мокротой"],
            "diagnostics": ["На рентгене инфильтративные изменения в верхней доле правого лёгкого",
                            "Мокрота на БК положительная"],
            "correct_diagnosis": "Инфильтративный туберкулёз лёгких"
        },
        DiseaseType.EPILEPSY: {
            "name": "Эпилепсия",
            "complaints": ["Периодические судорожные приступы", "Потеря сознания во время приступов",
                           "Чувство страха перед приступом"],
            "anamnesis": ["Первый приступ был год назад", "С тех пор приступы повторялись 2-3 раза"],
            "diagnostics": ["На ЭЭГ регистрируются эпилептические разряды", "МРТ без структурных изменений"],
            "correct_diagnosis": "Идиопатическая генерализованная эпилепсия"
        }
    }

def create_patient(disease_type: DiseaseType) -> Patient:


    if disease_type not in disease_data:
        raise ValueError("Unknown disease type")

    data = disease_data[disease_type]

    disease = Disease(
        name=data["name"],
        complaints=data["complaints"],
        anamnesis=data["anamnesis"],
        diagnostics=data["diagnostics"],
        correct_diagnosis=data["correct_diagnosis"]
    )

    ages = {
        DiseaseType.APPENDICITIS: random.randint(18, 40),
        DiseaseType.DIABETES: random.randint(45, 65),
        DiseaseType.ANEMIA: random.randint(25, 60),
        DiseaseType.TUBERCULOSIS: random.randint(25, 50),
        DiseaseType.EPILEPSY: random.randint(20, 35)
    }

    professions = ["Рабочий", "Офисный сотрудник", "Учитель", "Водитель", "Продавец"]

    return Patient(
        fio="Иванов Иван Иванович",
        gender="М",
        age=ages.get(disease_type, 30),
        profession=random.choice(professions),
        disease=disease
    )