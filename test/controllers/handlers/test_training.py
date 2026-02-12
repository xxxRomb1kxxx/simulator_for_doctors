import pytest
from unittest.mock import AsyncMock, Mock, patch
from aiogram.types import CallbackQuery, User
from aiogram.fsm.context import FSMContext
from controllers.handlers.training import (
    training,
    dialog_commands,
    control_case,
    start_case
)
from controllers.states.dialog import DialogState
from models.entities.disease import DiseaseType
from services.case_service import CaseInitResult


@pytest.mark.asyncio
class TestTrainingHandlers:

    @pytest.fixture
    def mock_callback(self):
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=12345, is_bot=False, first_name="Test")
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        return callback

    @pytest.fixture
    def mock_state(self):
        state = AsyncMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.get_data = AsyncMock(return_value={})
        state.set_state = AsyncMock()
        return state

    @pytest.fixture
    def mock_case_result(self):
        result = Mock(spec=CaseInitResult)
        result.patient = Mock()
        result.card = Mock()
        result.engine = Mock()
        return result

    async def test_training_menu(self, mock_callback):
        await training(mock_callback)

        mock_callback.answer.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        args, kwargs = mock_callback.message.answer.call_args
        assert "Выберите заболевание" in args[0]
        from controllers.keyboards.inline import training_menu
        assert kwargs.get("reply_markup") == training_menu()

    @patch('controllers.handlers.training.force_diagnosis')
    async def test_dialog_commands_diagnosis(self, mock_force_diagnosis, mock_callback, mock_state):
        mock_callback.data = "cmd:diagnosis"

        await dialog_commands(mock_callback, mock_state)

        mock_force_diagnosis.assert_called_once()
        mock_callback.answer.assert_called_once()

    @patch('controllers.handlers.training.finish_dialog')
    async def test_dialog_commands_finish(self, mock_finish_dialog, mock_callback, mock_state):
        mock_callback.data = "cmd:finish"

        await dialog_commands(mock_callback, mock_state)

        mock_finish_dialog.assert_called_once()
        mock_callback.answer.assert_called_once()

    @patch('controllers.handlers.training.CaseService')
    async def test_control_case(self, mock_case_service, mock_callback, mock_state, mock_case_result):
        mock_case_service.start_random_case.return_value = mock_case_result

        await control_case(mock_callback, mock_state)

        mock_case_service.start_random_case.assert_called_once()
        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once_with(DialogState.waiting_question)
        assert mock_callback.message.answer.call_count >= 2

    @patch('controllers.handlers.training.CaseService')
    async def test_start_case_valid(self, mock_case_service, mock_callback, mock_state, mock_case_result):
        mock_callback.data = "disease:diabetes"
        mock_case_service.start_case_by_type.return_value = mock_case_result

        await start_case(mock_callback, mock_state)

        mock_case_service.start_case_by_type.assert_called_once_with(DiseaseType.DIABETES)
        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once_with(DialogState.waiting_question)

    @patch('controllers.handlers.training.CaseService')
    async def test_start_case_invalid(self, mock_case_service, mock_callback, mock_state):
        mock_callback.data = "disease:invalid"
        mock_case_service.start_case_by_type.side_effect = ValueError()

        await start_case(mock_callback, mock_state)

        mock_callback.message.answer.assert_called_with("Ошибка: неизвестный тип заболевания")
        mock_state.update_data.assert_not_called()

    @pytest.mark.parametrize("disease_code,disease_type", [
        ("diabetes", DiseaseType.DIABETES),
        ("anemia", DiseaseType.ANEMIA),
        ("tuberculosis", DiseaseType.TUBERCULOSIS),
        ("appendicitis", DiseaseType.APPENDICITIS),
        ("epilepsy", DiseaseType.EPILEPSY),
    ])
    @patch('controllers.handlers.training.CaseService')
    async def test_start_case_all_diseases(self, mock_case_service, disease_code, disease_type,
                                           mock_callback, mock_state, mock_case_result):
        mock_callback.data = f"disease:{disease_code}"
        mock_case_service.start_case_by_type.return_value = mock_case_result

        await start_case(mock_callback, mock_state)

        mock_case_service.start_case_by_type.assert_called_once_with(disease_type)