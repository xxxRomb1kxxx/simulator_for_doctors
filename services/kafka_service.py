"""
Kafka-интеграция для simulator_for_doctors.

Топики:
  dialog-logs       — каждое сообщение врача и пациента
  diagnosis-results — результат проверки диагноза
  gigachat-errors   — ошибки при обращении к GigaChat
"""

import json
import logging
from typing import Any

from confluent_kafka import Producer

logger = logging.getLogger(__name__)

TOPIC_DIALOG_LOGS = "dialog-logs"
TOPIC_DIAGNOSIS_RESULTS = "diagnosis-results"
TOPIC_GIGACHAT_ERRORS = "gigachat-errors"

_producer: Producer | None = None


def get_producer() -> Producer:
    """Синглтон — создаёт Producer один раз при первом вызове."""
    global _producer
    if _producer is None:
        from config import get_settings
        settings = get_settings()

        _producer = Producer({
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "acks": "1",
            "retries": 3,
            "retry.backoff.ms": 500,
            "linger.ms": 10,
            "compression.type": "lz4",
        })
        logger.info("[Kafka] Producer initialized → %s", settings.kafka_bootstrap_servers)
    return _producer


def _delivery_report(err, msg) -> None:
    if err:
        logger.warning("[Kafka] Delivery failed: topic=%s err=%s", msg.topic(), err)
    else:
        logger.debug("[Kafka] Delivered: topic=%s partition=%d offset=%d",
                     msg.topic(), msg.partition(), msg.offset())


def send_event(topic: str, key: str, data: dict[str, Any]) -> None:
    """
    Отправить событие в Kafka. Fire-and-forget.
    Никогда не бросает исключений — бот не упадёт из-за Kafka.
    """
    try:
        producer = get_producer()
        producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            on_delivery=_delivery_report,
        )
        producer.poll(0)  # неблокирующий вызов для обработки колбэков
    except Exception as exc:
        logger.error("[Kafka] send_event failed: topic=%s key=%s err=%s", topic, key, exc)


def flush_producer() -> None:
    """Вызывать при shutdown — дожидается отправки всех буферизованных сообщений."""
    if _producer is not None:
        logger.info("[Kafka] Flushing producer...")
        _producer.flush(timeout=10)
        logger.info("[Kafka] Producer flushed.")