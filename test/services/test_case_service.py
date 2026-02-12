import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.case_service import CaseService, DialogResult, DiagnosisResult, CaseInitResult
from models.entities.disease import DiseaseType
from models.entities.patient import Patient
from models.entities.medical_card import MedicalCard
from dialog_engine.dialog_engine import DialogEngine
from models.entities.disease import Disease


class TestCaseService:
    """Тесты для сервиса клинических кейсов."""

    @patch('services.case_service.random.choice')
    @patch('services.case_service.CaseService._build_case')
    def test_start_random_case(self, mock_build_case, mock_choice):
        """Тест запуска случайного кейса."""
        mock_choice.return_value = DiseaseType.APPENDICITIS
        mock_build_case.return_value = CaseInitResult(
            patient=Mock(),
            card=Mock(),
            engine=Mock()
        )

        result = CaseService.start_random_case()

        mock_choice.assert_called_once_with(list(DiseaseType))
        mock_build_case.assert_called_once_with(DiseaseType.APPENDICITIS)
        assert isinstance(result, CaseInitResult)

    @patch('services.case_service.create_patient')
    @patch('services.case_service.MedicalCard')
    @patch('services.case_service.DialogEngine')
    def test_build_case(self, mock_dialog_engine, mock_medical_card, mock_create_patient):
        """Тест создания кейса."""
        # Создаем реальный объект болезни, а не мок
        from models.entities.disease import Disease

        mock_patient = Mock()
        mock_patient.fio = "Иванов Иван"

        # Создаем реальный объект Disease
        disease = Disease(
            name="Аппендицит",
            complaints=[],
            anamnesis=[],
            diagnostics=[],
            correct_diagnosis="Острый аппендицит"
        )
        mock_patient.disease = disease

        mock_create_patient.return_value = mock_patient

        mock_card = Mock(spec=MedicalCard)
        mock_medical_card.return_value = mock_card

        mock_engine = Mock(spec=DialogEngine)
        mock_dialog_engine.return_value = mock_engine

        result = CaseService._build_case(DiseaseType.APPENDICITIS)

        mock_create_patient.assert_called_once_with(DiseaseType.APPENDICITIS)
        mock_medical_card.assert_called_once()
        mock_dialog_engine.assert_called_once_with(mock_patient, mock_card)

        assert result.patient == mock_patient
        assert result.card == mock_card
        assert result.engine == mock_engine

    def test_process_dialog_normal(self):
        """Тест обычной обработки диалога."""
        mock_engine = Mock(spec=DialogEngine)
        mock_engine.process.return_value = "Как давно болит?"

        result = CaseService.process_dialog(mock_engine, "Болит живот")

        mock_engine.process.assert_called_once_with("Болит живот")
        assert result.answer_text == "Как давно болит?"
        assert result.should_ask_diagnosis is False
        assert result.prompt_text is None

    @pytest.mark.parametrize("command", ["/диагноз", "/diagnosis", "диагноз"])
    def test_process_dialog_with_diagnosis_command(self, command):
        """Тест обработки команды диагноза."""
        mock_engine = Mock(spec=DialogEngine)
        mock_engine.process.return_value = "Хорошо, ставьте диагноз"

        result = CaseService.process_dialog(mock_engine, command)

        mock_engine.process.assert_called_once_with(command)
        assert result.should_ask_diagnosis is True

    @patch('services.case_service.check')
    def test_check_diagnosis_correct(self, mock_check):
        """Тест проверки правильного диагноза."""
        mock_patient = Mock()
        mock_patient.disease.correct_diagnosis = "Острый аппендицит"
        mock_card = Mock(spec=MedicalCard)
        mock_card.render.return_value = "Медицинская карта"
        mock_check.return_value = True

        result = CaseService.check_diagnosis("Острый аппендицит", mock_patient, mock_card)

        mock_check.assert_called_once_with("Острый аппендицит", "Острый аппендицит")
        assert mock_card.diagnosis == "Острый аппендицит"
        assert result.is_correct is True
        assert result.message_text == "Диагноз верный!"
        assert result.rendered_card == "Медицинская карта"

    @patch('services.case_service.check')
    def test_check_diagnosis_incorrect(self, mock_check):
        """Тест проверки неправильного диагноза."""
        mock_patient = Mock()
        mock_patient.disease.correct_diagnosis = "Острый аппендицит"
        mock_card = Mock(spec=MedicalCard)
        mock_card.render.return_value = "Медицинская карта"
        mock_check.return_value = False

        result = CaseService.check_diagnosis("Гастрит", mock_patient, mock_card)

        mock_check.assert_called_once_with("Гастрит", "Острый аппендицит")
        assert result.is_correct is False
        assert "Неверно" in result.message_text
        assert "Острый аппендицит" in result.message_text

    def test_start_case_by_type(self):
        """Тест запуска кейса по типу заболевания."""
        with patch.object(CaseService, '_build_case') as mock_build:
            mock_build.return_value = CaseInitResult(
                patient=Mock(),
                card=Mock(),
                engine=Mock()
            )

            result = CaseService.start_case_by_type(DiseaseType.DIABETES)

            mock_build.assert_called_once_with(DiseaseType.DIABETES)
            assert isinstance(result, CaseInitResult)