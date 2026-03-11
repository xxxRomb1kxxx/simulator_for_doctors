"""
Воркер: читает запросы из Kafka-топика gigachat-req,
вызывает GigaChat и кладёт ответ в gigachat-res.
Количество воркеров = количество параллельных потоков к GigaChat.
"""
import json
import logging
import threading
import time
from confluent_kafka import Consumer, Producer

logger = logging.getLogger(__name__)

TOPIC_REQ = "gigachat-req"
TOPIC_RES = "gigachat-res"
BOOTSTRAP = "localhost:9092"
NUM_WORKERS = 3  # не больше чем rate-limit GigaChat


def process_one(msg_value: dict) -> dict:
    """Реальный вызов GigaChat. Подключаем твой существующий движок."""
    from giga.llm_response_generator import GigachatResponseGenerator

    user_id = msg_value["user_id"]
    context = msg_value["context"]
    history = msg_value["history"]
    disease = msg_value["disease"]
    complaints = msg_value["complaints"]

    llm = GigachatResponseGenerator(disease_name=disease, complaints=complaints)
    response = llm.generate(context=context, dialog_messages=history)

    return {
        "user_id": user_id,
        "text": response.text,
        "complaints": response.complaints,
        "anamnesis": response.anamnesis,
        "diagnostics": response.diagnostics,
    }


def worker_loop(worker_id: int):
    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP,
        "group.id": "gigachat-workers",
        "auto.offset.reset": "latest",
        "enable.auto.commit": False,
        "max.poll.interval.ms": 60000,
    })
    producer = Producer({"bootstrap.servers": BOOTSTRAP})

    consumer.subscribe([TOPIC_REQ])
    logger.info("[Worker %d] started", worker_id)

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error("[Worker %d] Kafka error: %s", worker_id, msg.error())
            continue

        try:
            data = json.loads(msg.value())
            result = process_one(data)

            producer.produce(
                TOPIC_RES,
                key=str(data["user_id"]).encode(),
                value=json.dumps(result, ensure_ascii=False).encode(),
            )
            producer.flush()
            consumer.commit(msg)
            logger.info("[Worker %d] processed user_id=%s", worker_id, data["user_id"])

        except Exception as e:
            logger.error("[Worker %d] failed: %s", worker_id, e)
            # НЕ делаем commit — сообщение вернётся в очередь
            time.sleep(1)


def start_workers():
    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=worker_loop, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    logger.info("Started %d GigaChat workers", NUM_WORKERS)
    return threads


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    threads = start_workers()
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        sys.exit(0)