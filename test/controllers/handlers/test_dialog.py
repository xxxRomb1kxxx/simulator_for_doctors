import pytest
from unittest.mock import AsyncMock, Mock, patch
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User
from controllers.handlers.dialog import (
    finish_dialog,
    force_diagnosis,
    dialog,
    diagnosis
)
from controllers.states.dialog import DialogState
from services.case_service import DialogResult, DiagnosisResult


@pytest.mark.asyncio
class TestDialogHandlers:


    @pytest.fixture
    def mock_message(self):
        message = AsyncMock(spec=Message)
        message.from_user = User(id=12345, is_bot=False, first_name="Test")
        message.text = "тест"
        message.answer = AsyncMock()
        return message

    @pytest.fixture
    def mock_state(self):
        state = AsyncMock(spec=FSMContext)
        state.get_data = AsyncMock()
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.clear = AsyncMock()
        return state

    async def test_finish_dialog(self, mock_message, mock_state):
        await finish_dialog(mock_message, mock_state)

        mock_state.clear.assert_called_once()
        assert mock_message.answer.call_count == 2
        mock_message.answer.assert_any_call("✅ Диалог завершен командой /завершить")
        mock_message.answer.assert_any_call("Для нового кейса нажмите /start")

    async def test_force_diagnosis_without_data(self, mock_message, mock_state):
        mock_state.get_data.return_value = {}

        await force_diagnosis(mock_message, mock_state)

        mock_state.set_state.assert_not_called()
        mock_message.answer.assert_called_once_with("Сначала начните кейс!")

    async def test_force_diagnosis_with_data(self, mock_message, mock_state):
        mock_state.get_data.return_value = {"patient": "test"}

        await force_diagnosis(mock_message, mock_state)

        mock_state.set_state.assert_called_once_with(DialogState.waiting_diagnosis)
        mock_message.answer.assert_called_once_with("📝 Теперь поставьте диагноз (напишите его текстом):")

    @patch('controllers.handlers.dialog.CaseService')
    async def test_dialog_process(self, mock_case_service, mock_message, mock_state):
        mock_state.get_data.return_value = {"engine": Mock()}
        mock_case_service.process_dialog.return_value = DialogResult(
            answer_text="Тестовый ответ",
            should_ask_diagnosis=False,
            prompt_text=None
        )

        await dialog(mock_message, mock_state)

        mock_case_service.process_dialog.assert_called_once()
        mock_message.answer.assert_called_once_with("Тестовый ответ")
        mock_state.set_state.assert_not_called()

    @patch('controllers.handlers.dialog.CaseService')
    async def test_dialog_with_diagnosis_request(self, mock_case_service, mock_message, mock_state):
        mock_state.get_data.return_value = {"engine": Mock()}
        mock_case_service.process_dialog.return_value = DialogResult(
            answer_text="Тестовый ответ",
            should_ask_diagnosis=True,
            prompt_text="Поставьте диагноз"
        )

        await dialog(mock_message, mock_state)

        mock_case_service.process_dialog.assert_called_once()
        mock_message.answer.assert_any_call("Тестовый ответ")
        mock_state.set_state.assert_called_once_with(DialogState.waiting_diagnosis)
        mock_message.answer.assert_any_call("Поставьте диагноз")

    @patch('controllers.handlers.dialog.CaseService')
    async def test_diagnosis_check(self, mock_case_service, mock_message, mock_state):
        mock_state.get_data.return_value = {
            "patient": Mock(),
            "card": Mock()
        }
        mock_case_service.check_diagnosis.return_value = DiagnosisResult(
            is_correct=True,
            message_text="Диагноз верный!",
            rendered_card="Медицинская карта пациента..."
        )

        await diagnosis(mock_message, mock_state)

        mock_case_service.check_diagnosis.assert_called_once()
        mock_message.answer.assert_any_call("Диагноз верный!")
        mock_message.answer.assert_any_call("Медицинская карта пациента...")
        mock_state.clear.assert_called_once()