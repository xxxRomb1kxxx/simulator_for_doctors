import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_gigachat import GigaChat
from config import get_settings
from giga.system_prompt import SystemPromptGenerator

logger = logging.getLogger(__name__)


def create_gigachat() -> GigaChat:
    settings = get_settings()
    logger.debug("Creating GigaChat instance")
    return GigaChat(
        credentials=settings.gigachat.giga_credentials,
        scope=settings.gigachat.giga_scope,
        model=settings.gigachat.giga_model,
        verify_ssl_certs=False,
        temperature=settings.gigachat.giga_temperature,
        timeout=settings.gigachat.giga_timeout,
        max_tokens=settings.gigachat.giga_max_tokens,
    )


@retry(
    retry=retry_if_exception_type((TimeoutError, ConnectionError, OSError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def _invoke_gigachat(messages: List[BaseMessage]) -> str:
    llm = create_gigachat()
    response = llm.invoke(messages)
    content = response.content or ""
    logger.info("LLM response received (%d chars)", len(content))
    return content.strip()


@dataclass
class PatientResponse:
    """Результат одного хода — ответ пациента + медданные для карты."""
    text: str
    complaints: list[str]
    anamnesis: list[str]
    diagnostics: list[str]


class IResponseGenerator(ABC):
    FALLBACK_RESPONSE = "Извините, я не совсем понял вопрос. Можете переформулировать?"

    @abstractmethod
    def generate(self, context: str, dialog_messages: list[dict]) -> PatientResponse:
        pass


class GigachatResponseGenerator(IResponseGenerator):

    def __init__(self, disease_name: str, complaints: list[str]) -> None:
        self.system_prompt = SystemPromptGenerator.get_system_prompt(disease_name, complaints)

    def generate(self, context: str, dialog_messages: list[dict]) -> PatientResponse:
        try:
            messages = self._build_messages(context, dialog_messages)
            logger.debug("Sending %d messages to GigaChat", len(messages))
            raw = _invoke_gigachat(messages)
            return self._parse(raw)
        except Exception:
            logger.exception("LLM generation failed after retries")
            return PatientResponse(
                text=self.FALLBACK_RESPONSE,
                complaints=[], anamnesis=[], diagnostics=[],
            )

    def _build_messages(self, context: str, dialog_messages: list[dict]) -> List[BaseMessage]:
        messages: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]

        history = dialog_messages[:-1] if len(dialog_messages) > 1 else []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        last = dialog_messages[-1] if dialog_messages else None
        if last and last["role"] == "user":
            recent_text = "\n".join(
                f"{'Врач' if m['role'] == 'user' else 'Пациент'}: {m['content']}"
                for m in history[-5:]
            ) or "Начало диалога"
            user_input = last["content"]
        else:
            recent_text = "Начало приёма"
            user_input = "Здравствуйте, на что жалуетесь?"

        prompt = SystemPromptGenerator.get_patient_response_prompt(
            context=context,
            history=recent_text,
            user_input=user_input,
        )
        messages.append(HumanMessage(content=prompt))
        return messages

    def _parse(self, raw: str) -> PatientResponse:
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data = json.loads(clean)
            return PatientResponse(
                text=str(data.get("reply", "") or self.FALLBACK_RESPONSE),
                complaints=  [str(x) for x in data.get("complaints",  []) if x],
                anamnesis=   [str(x) for x in data.get("anamnesis",   []) if x],
                diagnostics= [str(x) for x in data.get("diagnostics", []) if x],
            )
        except json.JSONDecodeError:
            logger.debug("LLM returned plain text, card extraction skipped")
            return PatientResponse(
                text=raw or self.FALLBACK_RESPONSE,
                complaints=[], anamnesis=[], diagnostics=[],
            )