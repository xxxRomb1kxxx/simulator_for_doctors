"""
dialog_engine.py — версия с Kafka-буфером для GigaChat.
Вместо прямого вызова LLM: пишем запрос в gigachat-req,
ждём ответа из gigachat-res с таймаутом.
"""
import json
import logging
import threading
import time
import uuid
from typing import Any

from confluent_kafka import Consumer, Producer
from config import get_settings
from giga.llm_response_generator import IResponseGenerator, PatientResponse
from models.models import MedicalCard, Patient

logger = logging.getLogger(__name__)

TOPIC_REQ = "gigachat-req"
TOPIC_RES = "gigachat-res"
RESPONSE_TIMEOUT = 30  # секунд ждём ответа от воркера


class KafkaLLM(IResponseGenerator):
    """
    Отправляет запрос в Kafka и ждёт ответа.
    Заменяет прямой вызов GigachatResponseGenerator.
    """
    FALLBACK = "Извините, не могу ответить прямо сейчас. Повторите вопрос."

    def __init__(self, disease_name: str, complaints: list[str], user_id: str) -> None:
        self.disease_name = disease_name
        self.complaints = complaints
        self.user_id = user_id
        settings = get_settings()
        self._producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})

    def generate(self, context: str, dialog_messages: list[dict]) -> PatientResponse:
        correlation_id = str(uuid.uuid4())

        # Отправляем запрос в очередь
        payload = {
            "user_id": self.user_id,
            "correlation_id": correlation_id,
            "context": context,
            "history": dialog_messages,
            "disease": self.disease_name,
            "complaints": self.complaints,
        }
        self._producer.produce(
            TOPIC_REQ,
            key=self.user_id.encode(),
            value=json.dumps(payload, ensure_ascii=False).encode(),
        )
        self._producer.flush()

        # Ждём ответа из gigachat-res
        response = self._wait_for_response(correlation_id)
        if response is None:
            logger.warning("[KafkaLLM] timeout for user=%s corr=%s", self.user_id, correlation_id)
            return PatientResponse(
                text=self.FALLBACK, complaints=[], anamnesis=[], diagnostics=[]
            )

        return PatientResponse(
            text=response.get("text", self.FALLBACK),
            complaints=response.get("complaints", []),
            anamnesis=response.get("anamnesis", []),
            diagnostics=response.get("diagnostics", []),
        )

    def _wait_for_response(self, correlation_id: str) -> dict | None:
        """Слушаем gigachat-res пока не придёт ответ с нашим correlation_id.

        ВАЖНО: auto.offset.reset=earliest — иначе при создании новой consumer group
        мы начнём читать только новые сообщения. Если воркер ответил раньше,
        чем мы подписались — ответ будет пропущен и бот всегда будет ждать таймаут.
        """
        settings = get_settings()
        consumer = Consumer({
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": f"bot-response-{self.user_id}-{correlation_id}",  # ← полный id, не [:8]
            "auto.offset.reset": "earliest",  # ← было "latest" — главный баг
            "enable.auto.commit": True,
        })
        consumer.subscribe([TOPIC_RES])
        deadline = time.monotonic() + RESPONSE_TIMEOUT

        try:
            while time.monotonic() < deadline:
                msg = consumer.poll(0.5)
                if msg is None or msg.error():
                    continue
                data = json.loads(msg.value())
                if data.get("correlation_id") == correlation_id:
                    return data
        finally:
            consumer.close()
        return None


class DialogEngine:
    """Управляет диалогом врача с пациентом-симулятором."""

    def __init__(
        self,
        patient: Patient,
        card: MedicalCard,
        user_id: str | None = None,
        llm: IResponseGenerator | None = None,
    ) -> None:
        self.patient = patient
        self.card = card
        self._stage = "greeting"
        self._history: list[dict[str, Any]] = []

        settings = get_settings()
        if llm is not None:
            self._llm = llm
        elif settings.kafka_enabled:
            # С Kafka — запросы буферизуются, GigaChat не перегружается
            self._llm = KafkaLLM(
                disease_name=patient.disease.name,
                complaints=patient.disease.complaints,
                user_id=user_id or "unknown",
            )
        else:
            # Без Kafka — прямой вызов как раньше
            from giga.llm_response_generator import GigachatResponseGenerator
            self._llm = GigachatResponseGenerator(
                disease_name=patient.disease.name,
                complaints=patient.disease.complaints,
            )
        logger.info("DialogEngine initialized for patient %s", patient.fio)

    def process(self, text: str) -> str:
        self._history.append({"role": "user", "content": text})

        if self._stage == "greeting":
            context = self._build_context(
                extra="Ты только что зашёл в кабинет врача. Это начало приёма."
            )
            self._stage = "dialog"
        else:
            context = self._build_context()

        result = self._llm.generate(
            context=context,
            dialog_messages=self._history[-20:],
        )

        self._history.append({"role": "assistant", "content": result.text})
        self._merge_into_card(result)
        return result.text

    def reset(self) -> None:
        self._stage = "greeting"
        self._history.clear()

    def _build_context(self, extra: str = "") -> str:
        p, d = self.patient, self.patient.disease
        ctx = (
            f"Информация о моей болезни:\n"
            f"  - Диагноз (скрыт от врача): {d.name}\n"
            f"  - Основные симптомы: {', '.join(d.complaints)}\n"
            f"  - История развития: {', '.join(d.anamnesis)}\n"
            f"  - Проведённые обследования: {', '.join(d.diagnostics)}\n\n"
            f"Мой профиль:\n"
            f"  - Возраст: {p.age}\n"
            f"  - Профессия: {p.profession}\n"
            f"  - Пол: {p.gender}\n"
        )
        if self.card.complaints:
            ctx += f"\nУже сообщённые жалобы: {', '.join(self.card.complaints)}"
        if extra:
            ctx += f"\n\nДополнительно: {extra}"
        return ctx

    def _merge_into_card(self, result) -> None:
        existing_complaints  = {x.lower() for x in self.card.complaints}
        existing_anamnesis   = {x.lower() for x in self.card.anamnesis}
        existing_diagnostics = {x.lower() for x in self.card.diagnostics}

        for item in result.complaints:
            if item and item.lower() not in existing_complaints:
                self.card.complaints.append(item)
                existing_complaints.add(item.lower())
        for item in result.anamnesis:
            if item and item.lower() not in existing_anamnesis:
                self.card.anamnesis.append(item)
                existing_anamnesis.add(item.lower())
        for item in result.diagnostics:
            if item and item.lower() not in existing_diagnostics:
                self.card.diagnostics.append(item)
                existing_diagnostics.add(item.lower())