"""
Kafka-интеграция для simulator_for_doctors.
"""
import asyncio
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
    """Синхронная отправка. Не бросает исключений."""
    try:
        producer = get_producer()
        producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            on_delivery=_delivery_report,
        )
        producer.poll(0)
    except Exception as exc:
        logger.error("[Kafka] send_event failed: topic=%s key=%s err=%s", topic, key, exc)

async def async_send_event(topic: str, key: str, data: dict[str, Any]) -> None:
    """
    Запускает send_event в executor — не блокирует event loop aiogram.
    Использовать эту версию везде, где вызов идёт из async-функции.
    """
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, send_event, topic, key, data)

def send_gigachat_error(user_id: str, error: str, context: dict[str, Any] | None = None) -> None:
    send_event(TOPIC_GIGACHAT_ERRORS, user_id, {
        "user_id": user_id,
        "error": error,
        **(context or {}),
    })

def flush_producer() -> None:
    if _producer is not None:
        logger.info("[Kafka] Flushing producer...")
        _producer.flush(timeout=10)
        logger.info("[Kafka] Producer flushed.")