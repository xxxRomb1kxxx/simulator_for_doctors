import pytest
from dialog_engine.dialog_engine import DialogEngine
from models.entities.patient import Patient
from models.entities.medical_card import MedicalCard
from models.entities.disease import Disease


class TestDialogEngine:

    @pytest.fixture
    def mock_patient(self):
        disease = Disease(
            name="Аппендицит",
            complaints=["Боль в животе"],
            anamnesis=["Болит 6 часов"],
            diagnostics=["УЗИ"],
            correct_diagnosis="Острый аппендицит"
        )
        return Patient(
            fio="Иванов Иван",
            gender="М",
            age=30,
            profession="Инженер",
            disease=disease
        )

    @pytest.fixture
    def mock_card(self):
        return MedicalCard()

    def test_engine_creation(self, mock_patient, mock_card):
        engine = DialogEngine(mock_patient, mock_card)
        assert engine is not None
        assert isinstance(engine, DialogEngine)

    def test_process_method_exists(self, mock_patient, mock_card):
        engine = DialogEngine(mock_patient, mock_card)
        assert hasattr(engine, 'process')
        assert callable(engine.process)

    def test_process_returns_string(self, mock_patient, mock_card):
        engine = DialogEngine(mock_patient, mock_card)
        result = engine.process("Тестовое сообщение")
        assert isinstance(result, str)