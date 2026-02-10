from langchain_gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from services.system_prompt import SystemPromptGenerator
from config.settings import settings


class LLMResponseGenerator:

    def __init__(self, disease_name: str, complaints: list):
        self.system_prompt = SystemPromptGenerator.get_system_prompt(
            disease_name, complaints
        )

        self.llm = GigaChat(
            credentials=settings.GIGA_CREDENTIALS,
            scope=settings.SCOPE,
            model="GigaChat",
            verify_ssl_certs=False,
            temperature=0.7,
            timeout=30,
            top_p=0.9,
            max_tokens=1000
        )

    def generate_response(self, context: str, history: str, user_input: str) -> str:
        formatted_prompt = SystemPromptGenerator.get_patient_response_prompt(
            context=context,
            history=history,
            user_input=user_input
        )
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=formatted_prompt),
        ]

        try:
            llm_response = self.llm.invoke(messages)
            return llm_response.content.strip()
        except Exception as e:
            print(f"Ошибка LLM: {e}")
            return "Извините, я не совсем понял вопрос. Можете переформулировать?"