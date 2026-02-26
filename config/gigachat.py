from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GigaChatSettings(BaseSettings):
    giga_credentials: str = Field(..., description="GigaChat API credentials (base64)")
    giga_scope: str = Field(default="GIGACHAT_API_PERS")
    giga_model: str = Field(default="GigaChat")
    giga_temperature: float = Field(default=0.9, ge=0.0, le=2.0)
    giga_max_tokens: int = Field(default=1500, ge=50, le=32000)
    giga_timeout: int = Field(default=30, ge=5, le=120)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )