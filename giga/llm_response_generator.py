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
    """Создаёт новый instance GigaChat"""
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
#
# @dataclass
# class PatientResponse:
#     text: str
#     complaints: list[str]
#     anamnesis: list[str]
#     diagnostics: list[str]

class IResponseGenerator(ABC):
    FALLBACK_RESPONSE = (
        "Извините, я не совсем понял вопрос. Можете переформулировать?"
    )

    @abstractmethod
    def generate_response(self, context: str, dialog_messages: list[dict],) -> str:
        pass

class ICardParser(ABC):

    @abstractmethod
    def extract_medical_data(self, doctor_question: str, patient_reply: str) -> dict:
        pass

class GigachatResponseGenerator(IResponseGenerator):

    def __init__(self, disease_name: str, complaints: list[str]) -> None:
        self.system_prompt = SystemPromptGenerator.get_system_prompt(disease_name,complaints,)

    def _build_messages(self,context: str, dialog_messages: list[dict]) -> List[BaseMessage]:
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

            prompt = SystemPromptGenerator.get_patient_response_prompt(
                context=context,
                history=recent_text,
                user_input=last["content"],
            )
        else:
            prompt = SystemPromptGenerator.get_patient_response_prompt(
                context=context,
                history="Начало приёма",
                user_input="Здравствуйте, на что жалуетесь?",
            )

        messages.append(HumanMessage(content=prompt))
        return messages

    def generate_response(self, context: str, dialog_messages: list[dict]) -> str:
        try:
            messages = self._build_messages(context, dialog_messages)
            logger.debug("Sending %d messages to GigaChat", len(messages))
            result = _invoke_gigachat(messages)
            return result or self.FALLBACK_RESPONSE
        except Exception:
            logger.exception("LLM generation failed after retries")
            return self.FALLBACK_RESPONSE


class GigachatCardParser(ICardParser):
    def extract_medical_data(self, doctor_question: str, patient_reply: str) -> dict:
        prompt = (
            "Ты медицинский ассистент. Извлеки данные из ответа пациента для медкарты.\n\n"
            f"Вопрос врача: {doctor_question}\n"
            f"Ответ пациента: {patient_reply}\n\n"
            "Верни ТОЛЬКО валидный JSON без пояснений:\n"
            "{\n"
            '  "complaints": ["жалоба 1"],\n'
            '  "anamnesis": ["факт анамнеза 1"],\n'
            '  "diagnostics": ["обследование 1"]\n'
            "}\n\n"
            "Правила:\n"
            "- complaints: текущие симптомы (боль, температура, слабость и т.д.)\n"
            "- anamnesis: история болезни (когда началось, как развивалось)\n"
            "- diagnostics: упомянутые анализы и обследования\n"
            "- Если данных нет — пустой список []\n"
            "- Кратко, от третьего лица: 'Жалуется на боль в животе'"
        )
        try:
            raw = _invoke_gigachat([HumanMessage(content=prompt)])
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(clean)
            return {
                "complaints": [str(x) for x in data.get("complaints", []) if x],
                "anamnesis": [str(x) for x in data.get("anamnesis", []) if x],
                "diagnostics": [str(x) for x in data.get("diagnostics", []) if x],
            }
        except Exception:
            logger.exception("extract_medical_data failed")
            return {"complaints": [], "anamnesis": [], "diagnostics": []}