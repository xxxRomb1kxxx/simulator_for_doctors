from models.entities.patient import Patient
from models.entities.disease import Disease
from models.entities.disease import DiseaseType

def create_patient(disease_type: DiseaseType) -> Patient:
    if disease_type == DiseaseType.APPENDICITIS:
        disease = Disease(
            name="Аппендицит",
            complaints=["Острая боль справа внизу живота", "Тошнота"],
            anamnesis=["Началось 6 часов назад"],
            diagnostics=["Лейкоцитоз", "Боль при пальпации"],
            correct_diagnosis="Аппендицит"
        )

    elif disease_type == DiseaseType.DIABETES:
        disease = Disease(
            name="Сахарный диабет",
            complaints=["Жажда", "Частое мочеиспускание"],
            anamnesis=["Постепенное начало"],
            diagnostics=["Глюкоза крови повышена"],
            correct_diagnosis="Сахарный диабет"
        )

    elif disease_type == DiseaseType.ANEMIA:
        disease = Disease(
            name="Анемия",
            complaints=["Слабость", "Головокружение"],
            anamnesis=["Хроническая усталость"],
            diagnostics=["Снижен гемоглобин"],
            correct_diagnosis="Анемия"
        )

    elif disease_type == DiseaseType.TUBERCULOSIS:
        disease = Disease(
            name="Туберкулез",
            complaints=["Кашель", "Похудение"],
            anamnesis=["Длительное течение"],
            diagnostics=["Изменения на рентгене"],
            correct_diagnosis="Туберкулез"
        )

    elif disease_type == DiseaseType.EPILEPSY:
        disease = Disease(
            name="Эпилепсия",
            complaints=["Судороги", "Потеря сознания"],
            anamnesis=["Приступы в анамнезе"],
            diagnostics=["Изменения на ЭЭГ"],
            correct_diagnosis="Эпилепсия"
        )

    else:
        raise ValueError("Unknown disease type")

    return Patient(
        fio="Иванов Иван Иванович",
        gender="М",
        age=30,
        profession="Рабочий",
        disease=disease
    )
