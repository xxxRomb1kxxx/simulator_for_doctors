import logging
import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Логирует каждый апдейт с временем выполнения."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        start = time.monotonic()

        update: Update | None = data.get("event_update")
        user = None
        if update:
            if update.message:
                user = update.message.from_user
            elif update.callback_query:
                user = update.callback_query.from_user

        user_info = f"user_id={user.id}" if user else "unknown"
        logger.debug("→ Update received [%s]", user_info)

        try:
            result = await handler(event, data)
            elapsed = (time.monotonic() - start) * 1000
            logger.debug("← Update handled [%s] in %.1fms", user_info, elapsed)
            return result
        except Exception:
            elapsed = (time.monotonic() - start) * 1000
            logger.exception("Update failed [%s] after %.1fms", user_info, elapsed)
            raise
