from models.entities.patient import Patient
from models.entities.disease import Disease

def create_appendicitis_patient():
    disease = Disease(
        name="Аппендицит",
        complaints=["Острая боль справа внизу живота", "Тошнота"],
        anamnesis=["Началось 6 часов назад"],
        diagnostics=["Лейкоцитоз", "Боль при пальпации"],
        correct_diagnosis="Аппендицит"
    )

    return Patient(
        fio="Иванов Иван Иванович",
        gender="М",
        age=24,
        profession="Студент",
        disease=disease
    )
