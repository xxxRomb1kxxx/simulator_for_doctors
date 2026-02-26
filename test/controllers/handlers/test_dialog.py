from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from telegram.handlers.dialog import finish_dialog, force_diagnosis, handle_diagnosis, handle_dialog
from telegram.states.dialog import DialogState
from services.case_service import DiagnosisResult, DialogResult


@pytest.mark.asyncio
class TestDialogHandlers:

    @pytest.fixture
    def mock_message(self) -> Message:
        msg = AsyncMock(spec=Message)
        msg.from_user = User(id=12345, is_bot=False, first_name="Test")
        msg.text = "тест"
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_state(self) -> FSMContext:
        state = AsyncMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={})
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.clear = AsyncMock()
        return state

    async def test_finish_dialog_clears_state(self, mock_message, mock_state) -> None:
        await finish_dialog(mock_message, mock_state)
        mock_state.clear.assert_called_once()
        mock_message.answer.assert_any_call("✅ Диалог завершён командой /завершить")
        mock_message.answer.assert_any_call("Для нового кейса нажмите /start")

    async def test_force_diagnosis_no_case(self, mock_message, mock_state) -> None:
        mock_state.get_data.return_value = {}
        await force_diagnosis(mock_message, mock_state)
        mock_state.set_state.assert_not_called()

    async def test_force_diagnosis_with_case(self, mock_message, mock_state) -> None:
        mock_state.get_data.return_value = {"patient": Mock()}
        await force_diagnosis(mock_message, mock_state)
        mock_state.set_state.assert_called_once_with(DialogState.waiting_diagnosis)

    @patch("telegram.handlers.dialog.CaseService")
    async def test_handle_dialog(self, mock_svc, mock_message, mock_state) -> None:
        mock_state.get_data.return_value = {"engine": Mock()}
        mock_svc.process_dialog.return_value = DialogResult(answer_text="Болит живот")

        await handle_dialog(mock_message, mock_state)

        mock_svc.process_dialog.assert_called_once()
        mock_message.answer.assert_called_once()

    @patch("telegram.handlers.dialog.CaseService")
    async def test_handle_dialog_no_engine(self, mock_svc, mock_message, mock_state) -> None:
        mock_state.get_data.return_value = {}
        await handle_dialog(mock_message, mock_state)
        mock_state.clear.assert_called_once()
        mock_svc.process_dialog.assert_not_called()

    @patch("telegram.handlers.dialog.CaseService")
    async def test_handle_diagnosis_correct(self, mock_svc, mock_message, mock_state) -> None:
        mock_state.get_data.return_value = {"patient": Mock(), "card": Mock()}
        mock_svc.check_diagnosis.return_value = DiagnosisResult(
            is_correct=True,
            message_text="✅ Диагноз верный!",
            rendered_card="📋 Карта",
            score=1.0,
        )

        await handle_diagnosis(mock_message, mock_state)

        mock_svc.check_diagnosis.assert_called_once()
        mock_message.answer.assert_any_call("✅ Диагноз верный!")
        mock_message.answer.assert_any_call("📋 Карта")
        mock_state.clear.assert_called_once()
