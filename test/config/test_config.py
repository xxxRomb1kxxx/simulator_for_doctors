import pytest
import os
from unittest.mock import patch
from config.settings import Settings
from config.logging import setup_logging


class TestConfig:

    @patch.dict(os.environ, {
        'GIGA_CREDENTIALS': 'test_creds',
        'ADMIN_IDS': '123456,789012'
    }, clear=True)
    def test_config_from_env(self):

        Settings._Settings__instance = None

        config = Settings()
        assert config.GIGA_CREDENTIALS == 'test_creds'
        if hasattr(config, 'ADMIN_IDS'):
            assert 123456 in config.ADMIN_IDS
            assert 789012 in config.ADMIN_IDS

    @patch.dict(os.environ, {
        'GIGA_CREDENTIALS': 'test_creds',
    }, clear=True)
    def test_config_without_optional(self):
        Settings._Settings__instance = None

        config = Settings()
        assert config.GIGA_CREDENTIALS == 'test_creds'

    @patch.dict(os.environ, {}, clear=True)
    def test_config_missing_required(self):

        Settings._Settings__instance = None

        config = Settings()
        assert config is not None
        assert hasattr(config, 'GIGA_CREDENTIALS')

    def test_singleton_pattern(self):
        Settings._Settings__instance = None

        config1 = Settings()
        config2 = Settings()
        assert config1 is config2

    @patch('logging.config.dictConfig')
    def test_setup_logging(self, mock_dictConfig):
        try:
            setup_logging(level='DEBUG')
            assert True
        except Exception as e:
            pytest.fail(f"setup_logging вызвал ошибку: {e}")