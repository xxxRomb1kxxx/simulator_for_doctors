import os
from unittest.mock import patch

import pytest

from config.logging import setup_logging


class TestSettings:

    def test_setup_logging_string_level(self) -> None:
        """Оригинальный баг: setup_logging(level: int) но тест передавал строку."""
        setup_logging("DEBUG")  # не должно падать
        setup_logging("INFO")
        setup_logging("WARNING")

    def test_settings_validation(self) -> None:
        """Pydantic выдаёт ошибку при отсутствии обязательных полей."""
        from config.settings import Settings

        with pytest.raises(Exception):
            # Без BOT_TOKEN и GIGA_CREDENTIALS должна быть ValidationError
            with patch.dict(os.environ, {}, clear=True):
                Settings()

    def test_settings_from_env(self) -> None:
        from config.settings import Settings

        env = {
            "BOT_TOKEN": "test_token",
            "GIGA_CREDENTIALS": "test_creds",
        }
        with patch.dict(os.environ, env, clear=True):
            s = Settings()
            assert s.bot_token == "test_token"
            assert s.giga_credentials == "test_creds"
            assert s.log_level == "INFO"  # default

    def test_invalid_log_level_raises(self) -> None:
        from config.settings import Settings

        env = {
            "BOT_TOKEN": "tok",
            "GIGA_CREDENTIALS": "creds",
            "LOG_LEVEL": "NONSENSE",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(Exception):
                Settings()
