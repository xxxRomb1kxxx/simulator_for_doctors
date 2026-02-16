import logging
from typing import List, Union
from langchain_gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from services.system_prompt import SystemPromptGenerator
from config.settings import settings

logger = logging.getLogger(__name__)

class LLMResponseGenerator:

    def __init__(self, disease_name: str, complaints: list):
        self.disease_name = disease_name
        self.complaints = complaints
        self.system_prompt = SystemPromptGenerator.get_system_prompt(
            disease_name, complaints
        )
        self.llm = GigaChat(
            credentials=settings.GIGA_CREDENTIALS,
            scope=settings.SCOPE,
            model="GigaChat",
            verify_ssl_certs=False,
            temperature=0.9,
            timeout=30,
            top_p=0.95,
            max_tokens=1500
        )

    def generate_response(self, context: str, dialog_messages: list) -> str:
        """
        Генерирует ответ с учётом всей истории диалога

        Args:
            context: Контекст болезни из PatientCardManager.get_disease_context()
            dialog_messages: Список сообщений с ролями [{"role": "user/assistant", "content": "..."}]
        """
        try:
            messages: List[BaseMessage] = []
            messages.append(SystemMessage(content=self.system_prompt))

            if dialog_messages and len(dialog_messages) > 0:
                history = dialog_messages[:-1] if len(dialog_messages) > 1 else []

                for msg in history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))

                last_message = dialog_messages[-1]
                if last_message["role"] == "user":
                    recent_history = "\n".join([
                        f"{'Врач' if m['role'] == 'user' else 'Пациент'}: {m['content']}"
                        for m in history[-5:]
                    ]) if history else "Начало диалога"

                    current_question = SystemPromptGenerator.get_patient_response_prompt(
                        context=context,
                        history=recent_history,
                        user_input=last_message["content"]
                    )
                    messages.append(HumanMessage(content=current_question))
            else:
                first_question = SystemPromptGenerator.get_patient_response_prompt(
                    context=context,
                    history="Начало приема",
                    user_input="Здравствуйте, на что жалуетесь?"
                )
                messages.append(HumanMessage(content=first_question))

            logger.debug(f"Отправляем {len(messages)} сообщений в GigaChat:")
            for i, msg in enumerate(messages):
                logger.debug(f"  {i}: {type(msg).__name__}")

            llm_response = self.llm.invoke(messages)

            logger.info(f"LLM call успешен, ответ: {len(llm_response.content or '')} символов")
            return llm_response.content.strip()

        except Exception as e:
            logger.exception(f"Ошибка LLM при генерации ответа: {e}")
            return "Извините, я не совсем понял вопрос. Можете переформулировать?"
