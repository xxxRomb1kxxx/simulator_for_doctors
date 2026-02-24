import logging
from typing import Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_gigachat import GigaChat
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import get_settings
from services.system_prompt import SystemPromptGenerator

logger = logging.getLogger(__name__)

# --- Singleton GigaChat клиент ---
_gigachat_client: Optional[GigaChat] = None


def _get_gigachat() -> GigaChat:
    """Возвращает единственный экземпляр GigaChat клиента (lazy init)."""
    global _gigachat_client
    if _gigachat_client is None:
        s = get_settings()
        _gigachat_client = GigaChat(
            credentials=s.giga_credentials,
            scope=s.giga_scope,
            model=s.giga_model,
            verify_ssl_certs=False,
            temperature=s.giga_temperature,
            timeout=s.giga_timeout,
            max_tokens=s.giga_max_tokens,
        )
        logger.info("GigaChat client initialized (model=%s)", s.giga_model)
    return _gigachat_client


class LLMResponseGenerator:

    FALLBACK_RESPONSE = "Извините, я не совсем понял вопрос. Можете переформулировать?"

    def __init__(self, disease_name: str, complaints: list[str]) -> None:
        self.system_prompt = SystemPromptGenerator.get_system_prompt(disease_name, complaints)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=False,
    )
    def _invoke_with_retry(self, messages: list[BaseMessage]) -> str:
        llm = _get_gigachat()
        response = llm.invoke(messages)
        content = response.content or ""
        logger.info("LLM response: %d chars", len(content))
        return content.strip()

    def generate_response(self, context: str, dialog_messages: list[dict]) -> str:
        """
        Генерирует ответ пациента с учётом истории диалога.

        Args:
            context: Контекст болезни из PatientCardManager.
            dialog_messages: История — список {"role": "user"|"assistant", "content": "..."}.

        Returns:
            Строка-ответ пациента или fallback при ошибке LLM.
        """
        try:
            messages: list[BaseMessage] = [SystemMessage(content=self.system_prompt)]

            # История — все сообщения кроме последнего
            history = dialog_messages[:-1] if len(dialog_messages) > 1 else []
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

            # Последнее сообщение врача — оборачиваем в prompt с контекстом
            last = dialog_messages[-1] if dialog_messages else None
            if last and last["role"] == "user":
                recent_text = "\n".join(
                    f"{'Врач' if m['role'] == 'user' else 'Пациент'}: {m['content']}"
                    for m in history[-5:]
                ) or "Начало диалога"

                prompt = SystemPromptGenerator.get_patient_response_prompt(
                    context=context,
                    history=recent_text,
                    user_input=last["content"],
                )
                messages.append(HumanMessage(content=prompt))
            else:
                # Первое сообщение
                prompt = SystemPromptGenerator.get_patient_response_prompt(
                    context=context,
                    history="Начало приёма",
                    user_input="Здравствуйте, на что жалуетесь?",
                )
                messages.append(HumanMessage(content=prompt))

            logger.debug("Sending %d messages to GigaChat", len(messages))
            result = self._invoke_with_retry(messages)
            return result or self.FALLBACK_RESPONSE

        except Exception:
            logger.exception("LLM generation failed after retries")
            return self.FALLBACK_RESPONSE
