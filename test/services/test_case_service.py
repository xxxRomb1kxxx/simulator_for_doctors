from unittest.mock import Mock, patch

import pytest

from models.entities.disease import DiseaseType
from models.entities.medical_card import MedicalCard
from models.entities.patient import Patient
from services.case_service import CaseInitResult, CaseService, DiagnosisResult, DialogResult


class TestCaseService:

    @patch("services.case_service.random.choice")
    @patch.object(CaseService, "_build_case")
    def test_start_random_case(self, mock_build, mock_choice) -> None:
        mock_choice.return_value = DiseaseType.APPENDICITIS
        mock_build.return_value = CaseInitResult(patient=Mock(), card=Mock(), engine=Mock())

        result = CaseService.start_random_case()

        mock_choice.assert_called_once_with(list(DiseaseType))
        mock_build.assert_called_once_with(DiseaseType.APPENDICITIS)
        assert isinstance(result, CaseInitResult)

    @patch.object(CaseService, "_build_case")
    def test_start_case_by_type(self, mock_build) -> None:
        mock_build.return_value = CaseInitResult(patient=Mock(), card=Mock(), engine=Mock())
        result = CaseService.start_case_by_type(DiseaseType.DIABETES)
        mock_build.assert_called_once_with(DiseaseType.DIABETES)
        assert isinstance(result, CaseInitResult)

    def test_process_dialog_normal(self) -> None:
        engine = Mock()
        engine.process.return_value = "Болит живот, доктор."

        result = CaseService.process_dialog(engine=engine, user_text="Где болит?")

        engine.process.assert_called_once_with("Где болит?")
        assert result.answer_text == "Болит живот, доктор."
        assert result.should_ask_diagnosis is False

    def test_process_dialog_never_sets_diagnosis_from_text(self) -> None:
        """
        В оригинале process_dialog проверял текст на '/диагноз' — это было лишним.
        Теперь решение принимает только FSM-хендлер.
        """
        engine = Mock()
        engine.process.return_value = "OK"

        # Даже если текст "/диагноз", process_dialog не должен менять флаг
        result = CaseService.process_dialog(engine=engine, user_text="/диагноз")
        assert result.should_ask_diagnosis is False

    @patch("services.case_service.check")
    @patch("services.case_service.similarity_score")
    def test_check_diagnosis_correct(self, mock_score, mock_check) -> None:
        mock_check.return_value = True
        mock_score.return_value = 1.0

        patient = Mock()
        patient.disease.correct_diagnosis = "Острый аппендицит"
        card = Mock(spec=MedicalCard)
        card.render.return_value = "📋 Карта"

        result = CaseService.check_diagnosis("Острый аппендицит", patient, card)

        assert result.is_correct is True
        assert "верный" in result.message_text.lower()
        assert result.rendered_card == "📋 Карта"
        assert result.score == 1.0
        assert card.diagnosis == "Острый аппендицит"

    @patch("services.case_service.check")
    @patch("services.case_service.similarity_score")
    def test_check_diagnosis_incorrect(self, mock_score, mock_check) -> None:
        mock_check.return_value = False
        mock_score.return_value = 0.2

        patient = Mock()
        patient.disease.correct_diagnosis = "Острый аппендицит"
        card = Mock(spec=MedicalCard)
        card.render.return_value = "📋 Карта"

        result = CaseService.check_diagnosis("Гастрит", patient, card)

        assert result.is_correct is False
        assert "Острый аппендицит" in result.message_text
        assert "20%" in result.message_text
