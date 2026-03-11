import logging
import sys

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .gigachat import GigaChatSettings
from .telegram import TelegramSettings

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"


class Settings(BaseSettings):
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    gigachat: GigaChatSettings = Field(default_factory=GigaChatSettings)

    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        description="Адрес Kafka. В Docker: kafka:9092",
    )
    kafka_enabled: bool = Field(
        default=True,
        description="false — отключить Kafka для локальной разработки",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return upper


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=logging.getLevelName(level),
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings