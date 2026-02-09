from models.intents.intents import detect_intent
from langchain_gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from services.system_prompt import SystemPromptGenerator
from models.entities.patient import Patient


class DialogEngine:
    def __init__(self, patient: Patient, card):
        self.patient = patient
        self.card = card
        self.stage = "greeting"
        self.dialog_history = []
        self.system_prompt = SystemPromptGenerator.get_system_prompt(
            patient.disease.name,
            patient.disease.complaints
        )

        self.llm = GigaChat(
            credentials="NjI3MzZiNmMtOWY3OS00MjNkLWEyOWUtYWMzZjk0ODYyMWI2OjRlZWM1N2Y1LWY4N2YtNDdiMi05OWZlLWZlNmYwYTFkY2YxMw==",
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
            verify_ssl_certs=False,
            temperature=0.7,
            timeout=30,
            top_p=0.9,
            max_tokens=1000
        )

    def process(self, text: str) -> str:
        text_lower = text.lower()
        self.dialog_history.append(f"{text}")

        if self.stage == "greeting":
            if any(w in text_lower for w in ["проходи", "сад", "да", "можно", "входите"]):
                self.stage = "dialog"
                response = "Здравствуйте, доктор. Спасибо, что приняли меня. У меня есть некоторые проблемы со здоровьем, которые меня беспокоят."
                self.dialog_history.append(f"{response}")
                return response
            response = "Добрый день, доктор. Можно войти на приём?"
            self.dialog_history.append(f"{response}")
            return response

        intent = detect_intent(text_lower)

        if intent in ["complaints", "anamnesis", "diagnostics", "diagnosis"]:
            return self._handle_intent_response(intent, text_lower)

        return self._generate_llm_response(text_lower)

    def _handle_intent_response(self, intent: str, text: str) -> str:
        """Обработка конкретных интентов с расширенными ответами"""
        if intent == "complaints":
            self.card.complaints = self.patient.disease.complaints
            complaints_text = ", ".join(self.card.complaints)
            response = f"Из основных жалоб: {complaints_text}. "
            response += self._enrich_with_experience("жалобы")

        elif intent == "anamnesis":
            self.card.anamnesis = self.patient.disease.anamnesis
            anamnesis_text = ", ".join(self.card.anamnesis)
            response = f"Если говорить о том, как всё началось: {anamnesis_text}. "
            response += self._enrich_with_experience("анамнез")

        elif intent == "diagnostics":
            self.card.diagnostics = self.patient.disease.diagnostics
            diag_text = ", ".join(self.card.diagnostics)
            response = f"Из обследований: {diag_text}. "
            response += self._enrich_with_experience("диагностика")

        elif intent == "diagnosis":
            response = "Я не врач, чтобы ставить диагноз. По моим симптомам - сильная жажда, частое мочеиспускание, слабость. Как вы думаете, что это может быть?"

            # Можно добавить более эмоциональную реакцию:
            # response = "Доктор, я очень переживаю! У меня такие странные симптомы: постоянно хочется пить, бегаю в туалет каждые полчаса, совсем нет сил. Что это может быть? Я боюсь, что это что-то серьёзное..."

        self.dialog_history.append(f"Пациент: {response}")
        return response
    def _enrich_with_experience(self, category: str) -> str:
        """Добавляет субъективный опыт пациента в зависимости от болезни"""
        disease_name = self.patient.disease.name

        if disease_name == "Аппендицит":
            if category == "жалобы":
                return "Боль особенно усиливается при движении. Иногда кажется, что живот вот-вот лопнет."
            elif category == "анамнез":
                return "Сначала думал, что это просто расстройство желудка, но боль не проходила."

        elif disease_name == "Сахарный диабет":
            if category == "жалобы":
                return "Постоянно хочется пить, даже ночью просыпаюсь от жажды. И в туалет бегаю каждые полчаса."

        elif disease_name == "Анемия":
            if category == "жалобы":
                return "Даже подняться по лестнице на второй этаж - уже одышка. Голова кружится, когда резко встаю."

        elif disease_name == "Туберкулёз":
            if category == "жалобы":
                return "Кашель сухой, особенно по ночам. За последний месяц похудел килограмма на три, хотя аппетит вроде нормальный."

        elif disease_name == "Эпилепсия":
            if category == "анамнез":
                return "Первый приступ был год назад. С тех пор стараюсь не оставаться один, боюсь повторения."

        return "Это доставляет мне серьёзный дискомфорт в повседневной жизни."

    def _generate_llm_response(self, text: str) -> str:
        """Генерация ответа через LLM с полным контекстом"""
        context = "\n".join(self.dialog_history[-10:])  # 10 последних реплик

        disease_context = f"""
        Информация о моей болезни:
        - Диагноз: {self.patient.disease.name}
        - Основные симптомы: {', '.join(self.patient.disease.complaints)}
        - История развития: {', '.join(self.patient.disease.anamnesis)}
        - Проведённые обследования: {', '.join(self.patient.disease.diagnostics)}

        Мой профиль:
        - Возраст: {self.patient.age}
        - Профессия: {self.patient.profession}
        - Пол: {self.patient.gender}
        """
        full_prompt = f"""Контекст болезни:
        {disease_context}

        История диалога:
        {context}

        Врач спрашивает: {text}

        Как мне, как пациенту, ответить на этот вопрос? 
        Инструкции для ответа:
        1. Отвечай от первого лица, будь естественным
        2. Опиши свои ощущения и переживания
        3. Отвечай кратко (1-3 предложения), но ёмко
        4. Не ставь диагноз сам, только описывай симптомы
        5. Будь эмоционально вовлечённым, но не драматизируй"""



        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=full_prompt),
        ]

        try:
            llm_response = self.llm.invoke(messages)
            response = llm_response.content.strip()
            self.dialog_history.append(f"{response}")
            return response
        except Exception as e:
            print(f"Ошибка LLM: {e}")
            fallback = "Извините, я не совсем понял вопрос. Можете переформулировать?"
            self.dialog_history.append(f"{fallback}")
            return fallback