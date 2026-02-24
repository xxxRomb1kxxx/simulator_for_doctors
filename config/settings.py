from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str = Field(..., description="Telegram Bot Token")
    giga_credentials: str = Field(..., description="GigaChat API credentials (base64)")
    giga_scope: str = Field(
        default="GIGACHAT_API_PERS",
        description="GigaChat API scope",
    )
    giga_model: str = Field(default="GigaChat", description="GigaChat model name")
    giga_temperature: float = Field(default=0.9, ge=0.0, le=2.0)
    giga_max_tokens: int = Field(default=1500, ge=50, le=32000)
    giga_timeout: int = Field(default=30, ge=5, le=120)

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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Возвращает синглтон настроек (кешируется через lru_cache)."""
    return Settings()


settings = get_settings()
