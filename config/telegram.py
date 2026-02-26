from pydantic import Field
from .base import BaseAppSettings


class TelegramSettings(BaseAppSettings):
    bot_token: str = Field(..., description="Telegram Bot Token")