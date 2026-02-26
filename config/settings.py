from functools import lru_cache

from .telegram import TelegramSettings
from .gigachat import GigaChatSettings
from .logging import LoggingSettings, setup_logging

import logging

class Settings:
    def __init__(self) -> None:
        self.telegram = TelegramSettings()
        self.gigachat = GigaChatSettings()
        self.logging = LoggingSettings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

setup_logging(level=logging.getLevelName(settings.logging.log_level))