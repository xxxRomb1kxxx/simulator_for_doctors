import pytest
from unittest.mock import AsyncMock
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, BotCommand
from telegram.keyboards.inline import (
    main_menu,
    training_menu,
    dialog_control_keyboard,
    get_main_kb,
    set_bot_commands
)


class TestKeyboards:

    def test_main_menu(self):
        keyboard = main_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2

        assert keyboard.inline_keyboard[0][0].text == "Тренировка"
        assert keyboard.inline_keyboard[0][0].callback_data == "training"

        assert keyboard.inline_keyboard[1][0].text == "Контрольный кейс"
        assert keyboard.inline_keyboard[1][0].callback_data == "control_case"

    def test_training_menu(self):
        keyboard = training_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 5

        diseases = {
            "diabetes": "Сахарный диабет",
            "anemia": "Анемия",
            "tuberculosis": "Туберкулез",
            "appendicitis": "Аппендицит",
            "epilepsy": "Эпилепсия"
        }

        for i, (code, name) in enumerate(diseases.items()):
            assert keyboard.inline_keyboard[i][0].text == name
            assert keyboard.inline_keyboard[i][0].callback_data == f"disease:{code}"

    def test_dialog_control_keyboard(self):
        keyboard = dialog_control_keyboard()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2

        assert keyboard.inline_keyboard[0][0].text == "🏥 Поставить диагноз"
        assert keyboard.inline_keyboard[0][0].callback_data == "cmd:diagnosis"

        assert keyboard.inline_keyboard[1][0].text == "✅ Завершить"
        assert keyboard.inline_keyboard[1][0].callback_data == "cmd:finish"

    def test_get_main_kb(self):
        keyboard = get_main_kb()

        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.keyboard[0][0].text == "🏥 Тренажер"
        assert keyboard.keyboard[1][0].text == "ℹ️ Помощь"
        assert keyboard.resize_keyboard is True

    @pytest.mark.asyncio
    async def test_set_bot_commands(self):
        mock_bot = AsyncMock()

        await set_bot_commands(mock_bot)

        mock_bot.set_my_commands.assert_called_once()
        commands = mock_bot.set_my_commands.call_args[0][0]

        assert len(commands) == 4
        assert isinstance(commands[0], BotCommand)
        assert commands[0].command == "start"
        assert commands[1].command == "help"
        assert commands[2].command == "завершить"
        assert commands[3].command == "диагноз"