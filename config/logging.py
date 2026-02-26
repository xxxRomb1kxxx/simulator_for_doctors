from pydantic import Field, field_validator
from .base import BaseAppSettings

import logging
import sys

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

class LoggingSettings(BaseAppSettings):
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()

        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")

        return upper