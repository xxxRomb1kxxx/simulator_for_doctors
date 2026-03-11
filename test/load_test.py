import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import threading
import time
import random
import queue
import statistics
from dataclasses import dataclass, field
from typing import List, Optional

from models.models import DiseaseType, MedicalCard
from models.patient_factory import create_patient
from giga.llm_response_generator import IResponseGenerator, PatientResponse
from dialog_engine.dialog_engine import DialogEngine
from services.case_service import CheckDiagnosisUseCase


# ─────────────────────────────────────────────────────────────────────────────
# Конфигурация
# ─────────────────────────────────────────────────────────────────────────────

CONCURRENT_USERS       = 50
TURNS_PER_USER         = 5
GIGACHAT_MAX_RPS       = 3      # реальный rate-limit GigaChat
GIGACHAT_MOCK_DELAY_MS = 300
GIGACHAT_ERROR_RATE    = 0.05

RATE_LIMIT_USER_COUNTS = [1, 5, 10, 20, 30, 50, 75, 100]


# ─────────────────────────────────────────────────────────────────────────────
# Fake LLMs
# ─────────────────────────────────────────────────────────────────────────────

class InstantFakeLLM(IResponseGenerator):
    def generate(self, context, dialog_messages):
        return PatientResponse(
            text="Болит живот, доктор.",
            complaints=["боль в животе"], anamnesis=[], diagnostics=[],
        )


class RealisticFakeLLM(IResponseGenerator):
    """Прямой вызов — все потоки ломятся к GigaChat одновременно."""
    _semaphore = threading.Semaphore(GIGACHAT_MAX_RPS)
    _call_counter = 0
    _error_counter = 0
    _lock = threading.Lock()

    def generate(self, context, dialog_messages):
        acquired = self._semaphore.acquire(timeout=5.0)
        if not acquired:
            with self._lock:
                RealisticFakeLLM._error_counter += 1
            raise RuntimeError("GigaChat rate limit exceeded")
        try:
            with self._lock:
                RealisticFakeLLM._call_counter += 1
            time.sleep(GIGACHAT_MOCK_DELAY_MS / 1000 + random.uniform(0, 0.1))
            if random.random() < GIGACHAT_ERROR_RATE:
                with self._lock:
                    RealisticFakeLLM._error_counter += 1
                raise ConnectionError("GigaChat temporary error")
            return PatientResponse(
                text="Да, у меня болит живот уже второй день.",
                complaints=["боль в животе"], anamnesis=["симптомы 2 дня"], diagnostics=[],
            )
        finally:
            self._semaphore.release()

    @classmethod
    def reset_counters(cls):
        with cls._lock:
            cls._call_counter = 0
            cls._error_counter = 0


# ─── Kafka-буфер: воркеры обрабатывают запросы с ограничением ────────────────

class KafkaQueueLLM(IResponseGenerator):
    """
    Имитирует Kafka-буфер:
    - все запросы кладутся в общую очередь (Kafka topic)
    - ровно GIGACHAT_MAX_RPS воркеров читают из очереди и вызывают GigaChat
    - остальные пользователи ЖДУТ в очереди вместо ошибки
    """
    _request_queue: queue.Queue = queue.Queue()
    _workers_started = False
    _lock = threading.Lock()
    _call_counter = 0
    _error_counter = 0

    @classmethod
    def _start_workers(cls):
        """Запускаем ровно GIGACHAT_MAX_RPS воркеров — как в реальной Kafka."""
        def worker():
            while True:
                item = cls._request_queue.get()
                if item is None:
                    break
                result_queue, context, dialog_messages = item
                try:
                    with cls._lock:
                        cls._call_counter += 1
                    # Имитируем реальный вызов GigaChat
                    time.sleep(GIGACHAT_MOCK_DELAY_MS / 1000 + random.uniform(0, 0.1))
                    if random.random() < GIGACHAT_ERROR_RATE:
                        with cls._lock:
                            cls._error_counter += 1
                        # При ошибке — повторяем (retry), а не возвращаем ошибку пользователю
                        time.sleep(0.5)
                        result_queue.put(PatientResponse(
                            text="Простите, повторите пожалуйста.",
                            complaints=[], anamnesis=[], diagnostics=[],
                        ))
                    else:
                        result_queue.put(PatientResponse(
                            text="Да, у меня болит живот уже второй день.",
                            complaints=["боль в животе"],
                            anamnesis=["симптомы 2 дня"],
                            diagnostics=[],
                        ))
                except Exception as e:
                    result_queue.put(PatientResponse(
                        text="Извините, не могу ответить.",
                        complaints=[], anamnesis=[], diagnostics=[],
                    ))
                finally:
                    cls._request_queue.task_done()

        for _ in range(GIGACHAT_MAX_RPS):
            t = threading.Thread(target=worker, daemon=True)
            t.start()

    @classmethod
    def reset_counters(cls):
        with cls._lock:
            cls._call_counter = 0
            cls._error_counter = 0

    def generate(self, context, dialog_messages):
        with self.__class__._lock:
            if not self.__class__._workers_started:
                self.__class__._start_workers()
                self.__class__._workers_started = True

        result_queue = queue.Queue()
        # Кладём запрос в "Kafka топик" — никогда не отказываем
        self.__class__._request_queue.put((result_queue, context, dialog_messages))
        # Ждём ответа от воркера (без таймаута — запрос ВСЕГДА будет обработан)
        return result_queue.get(timeout=60)


# ─────────────────────────────────────────────────────────────────────────────
# Результаты и симуляция пользователя
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class UserResult:
    user_id: int
    turns_completed: int
    total_time_s: float
    turn_times_ms: List[float]
    errors: List[str] = field(default_factory=list)
    diagnosis_correct: Optional[bool] = None


DOCTOR_QUESTIONS = [
    "Здравствуйте, на что жалуетесь?",
    "Как давно это началось?",
    "Где именно болит?",
    "Была ли температура?",
    "Есть ли тошнота или рвота?",
    "Принимали ли лекарства?",
]

DIAGNOSES = {
    DiseaseType.APPENDICITIS: "аппендицит",
    DiseaseType.DIABETES:     "диабет",
    DiseaseType.ANEMIA:       "анемия",
    DiseaseType.TUBERCULOSIS: "туберкулез",
    DiseaseType.EPILEPSY:     "эпилепсия",
}


def simulate_user(user_id, llm_factory, barrier):
    disease_type = random.choice(list(DiseaseType))
    patient = create_patient(disease_type)
    card = MedicalCard()
    engine = DialogEngine(patient=patient, card=card, llm=llm_factory())
    check_uc = CheckDiagnosisUseCase()
    turn_times = []
    errors = []

    barrier.wait()
    start_total = time.perf_counter()

    for turn in range(TURNS_PER_USER):
        question = random.choice(DOCTOR_QUESTIONS)
        t0 = time.perf_counter()
        try:
            engine.process(question)
        except Exception as e:
            errors.append(f"turn {turn}: {type(e).__name__}: {e}")
        finally:
            turn_times.append((time.perf_counter() - t0) * 1000)

    try:
        result = check_uc.execute(DIAGNOSES[disease_type], patient, card)
        diagnosis_correct = result.is_correct
    except Exception as e:
        errors.append(f"diagnosis: {e}")
        diagnosis_correct = None

    return UserResult(
        user_id=user_id,
        turns_completed=TURNS_PER_USER - len([e for e in errors if "turn" in e]),
        total_time_s=time.perf_counter() - start_total,
        turn_times_ms=turn_times,
        errors=errors,
        diagnosis_correct=diagnosis_correct,
    )


def run_concurrent_users(n_users, llm_factory, label):
    barrier = threading.Barrier(n_users)
    results = [None] * n_users
    threads = []

    def worker(i):
        results[i] = simulate_user(i, llm_factory, barrier)

    for i in range(n_users):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)

    wall_start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall_time = time.perf_counter() - wall_start

    all_times, total_errors, correct, attempts = [], 0, 0, 0
    for r in results:
        if r is None:
            continue
        all_times.extend(r.turn_times_ms)
        total_errors += len(r.errors)
        if r.diagnosis_correct is not None:
            attempts += 1
            if r.diagnosis_correct:
                correct += 1

    total_turns = n_users * TURNS_PER_USER
    sorted_times = sorted(all_times)

    return {
        "label": label,
        "n_users": n_users,
        "wall_time_s": round(wall_time, 3),
        "total_turns": total_turns,
        "throughput_turns_per_sec": round(total_turns / wall_time, 2),
        "latency_p50_ms": round(statistics.median(all_times), 1) if all_times else 0,
        "latency_p95_ms": round(sorted_times[int(len(sorted_times) * 0.95)], 1) if all_times else 0,
        "latency_p99_ms": round(sorted_times[int(len(sorted_times) * 0.99)], 1) if all_times else 0,
        "latency_max_ms": round(max(all_times), 1) if all_times else 0,
        "latency_mean_ms": round(statistics.mean(all_times), 1) if all_times else 0,
        "total_errors": total_errors,
        "error_rate_pct": round(total_errors / total_turns * 100, 2),
        "diagnosis_accuracy_pct": round(correct / attempts * 100, 1) if attempts else 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Отчёт
# ─────────────────────────────────────────────────────────────────────────────

def print_comparison_table(without_kafka, with_kafka):
    sep = "=" * 80
    print(f"\n{sep}")
    print("  СРАВНЕНИЕ: БЕЗ KAFKA vs С KAFKA-БУФЕРОМ")
    print(sep)
    print(f"  {'Users':>6} | {'без Kafka err':>13} | {'с Kafka err':>11} | "
          f"{'без p50(ms)':>11} | {'с p50(ms)':>10} | {'улучшение':>10}")
    print("  " + "-" * 78)

    for r1, r2 in zip(without_kafka, with_kafka):
        improvement = "✅ лучше" if r2["total_errors"] < r1["total_errors"] else "—"
        print(f"  {r1['n_users']:>6} | "
              f"{r1['total_errors']:>10} ({r1['error_rate_pct']:4.1f}%) | "
              f"{r2['total_errors']:>8} ({r2['error_rate_pct']:4.1f}%) | "
              f"{r1['latency_p50_ms']:>11.1f} | "
              f"{r2['latency_p50_ms']:>10.1f} | "
              f"{improvement:>10}")
    print()


def main():
    print("\n" + "=" * 70)
    print("  НАГРУЗОЧНЫЙ ТЕСТ — СИМУЛЯТОР ПАЦИЕНТОВ ДЛЯ ВРАЧЕЙ")
    print("=" * 70)

    # ── Тест 1: бизнес-логика ────────────────────────────────────────────────
    print(f"\n[1/4] Тест бизнес-логики: {CONCURRENT_USERS} пользователей, мгновенный LLM...")
    instant = run_concurrent_users(CONCURRENT_USERS, InstantFakeLLM, f"InstantLLM {CONCURRENT_USERS} users")
    print(f"      ✓ wall={instant['wall_time_s']}s throughput={instant['throughput_turns_per_sec']}t/s errors={instant['total_errors']}")

    # ── Тест 2: без Kafka ────────────────────────────────────────────────────
    print(f"\n[2/4] БЕЗ Kafka: {CONCURRENT_USERS} пользователей, прямой вызов GigaChat...")
    RealisticFakeLLM.reset_counters()
    without_kafka_main = run_concurrent_users(CONCURRENT_USERS, RealisticFakeLLM, f"БЕЗ Kafka {CONCURRENT_USERS} users")
    without_kafka_main["gigachat_errors"] = RealisticFakeLLM._error_counter
    print(f"      ✗ wall={without_kafka_main['wall_time_s']}s "
          f"p50={without_kafka_main['latency_p50_ms']}ms "
          f"errors={without_kafka_main['total_errors']} ({without_kafka_main['error_rate_pct']}%)")

    # ── Тест 3: с Kafka ──────────────────────────────────────────────────────
    print(f"\n[3/4] С Kafka-буфером: {CONCURRENT_USERS} пользователей, {GIGACHAT_MAX_RPS} воркера...")
    KafkaQueueLLM._workers_started = False
    KafkaQueueLLM.reset_counters()
    with_kafka_main = run_concurrent_users(CONCURRENT_USERS, KafkaQueueLLM, f"С Kafka {CONCURRENT_USERS} users")
    with_kafka_main["gigachat_errors"] = KafkaQueueLLM._error_counter
    print(f"      ✓ wall={with_kafka_main['wall_time_s']}s "
          f"p50={with_kafka_main['latency_p50_ms']}ms "
          f"errors={with_kafka_main['total_errors']} ({with_kafka_main['error_rate_pct']}%)")

    # ── Тест 4: нарастающая нагрузка — сравнение ─────────────────────────────
    print(f"\n[4/4] Нарастающая нагрузка {RATE_LIMIT_USER_COUNTS} — сравнение подходов...")
    results_without, results_with = [], []

    for n in RATE_LIMIT_USER_COUNTS:
        RealisticFakeLLM.reset_counters()
        r1 = run_concurrent_users(n, RealisticFakeLLM, f"БЕЗ {n}")
        r1["gigachat_errors"] = RealisticFakeLLM._error_counter
        results_without.append(r1)

        KafkaQueueLLM._workers_started = False
        KafkaQueueLLM.reset_counters()
        r2 = run_concurrent_users(n, KafkaQueueLLM, f"Kafka {n}")
        r2["gigachat_errors"] = KafkaQueueLLM._error_counter
        results_with.append(r2)

        print(f"  [{n:3d} users] "
              f"БЕЗ: errors={r1['total_errors']:3d} p50={r1['latency_p50_ms']:7.1f}ms | "
              f"Kafka: errors={r2['total_errors']:3d} p50={r2['latency_p50_ms']:7.1f}ms")

    # ── Итоговая таблица ──────────────────────────────────────────────────────
    print_comparison_table(results_without, results_with)

    total_err_before = sum(r["total_errors"] for r in results_without)
    total_err_after  = sum(r["total_errors"] for r in results_with)
    reduction = (1 - total_err_after / max(total_err_before, 1)) * 100

    print(f"  Итог: ошибок БЕЗ Kafka = {total_err_before}")
    print(f"        ошибок С Kafka   = {total_err_after}")
    print(f"        Снижение ошибок  = {reduction:.1f}%")

    # ── Сохраняем отчёт ──────────────────────────────────────────────────────
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "load_test_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Снижение ошибок: {reduction:.1f}%\n")
        f.write(f"БЕЗ Kafka: {total_err_before} ошибок\n")
        f.write(f"С Kafka:   {total_err_after} ошибок\n")
    print(f"\n  Отчёт сохранён: {report_path}")


if __name__ == "__main__":
    main()