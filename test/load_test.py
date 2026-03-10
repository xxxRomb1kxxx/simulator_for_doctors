import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import threading
import time
import random
import json
import statistics
from dataclasses import dataclass, field
from typing import List, Optional
from unittest.mock import patch

from models.models import DiseaseType, MedicalCard
from models.patient_factory import create_patient
from giga.llm_response_generator import IResponseGenerator, PatientResponse
from dialog_engine.dialog_engine import DialogEngine
from services.case_service import (
    CaseRepository, StartCaseUseCase, CheckDiagnosisUseCase, ProcessDialogUseCase
)


# ─────────────────────────────────────────────────────────────────────────────
# Configurable parameters
# ─────────────────────────────────────────────────────────────────────────────

CONCURRENT_USERS       = 50       # одновременных пользователей
TURNS_PER_USER         = 5        # ходов диалога на пользователя
GIGACHAT_MAX_RPS       = 3        # имитируем ограничение GigaChat (запросов/сек)
GIGACHAT_MOCK_DELAY_MS = 300      # имитируем задержку GigaChat (ms)
GIGACHAT_ERROR_RATE    = 0.05     # вероятность ошибки GigaChat (5%)

# Для теста предельной нагрузки GigaChat
RATE_LIMIT_USER_COUNTS = [1, 5, 10, 20, 30, 50, 75, 100]


# ─────────────────────────────────────────────────────────────────────────────
# Fake LLMs
# ─────────────────────────────────────────────────────────────────────────────

class InstantFakeLLM(IResponseGenerator):
    """Мгновенный ответ — тест чистой бизнес-логики без задержек."""

    def generate(self, context: str, dialog_messages: list[dict]) -> PatientResponse:
        return PatientResponse(
            text="Болит живот, доктор.",
            complaints=["боль в животе"],
            anamnesis=[],
            diagnostics=[],
        )


class RealisticFakeLLM(IResponseGenerator):
    """
    Имитирует реальный GigaChat:
    - задержка GIGACHAT_MOCK_DELAY_MS
    - rate-limit: не более GIGACHAT_MAX_RPS параллельных вызовов
    - случайные ошибки GIGACHAT_ERROR_RATE
    """
    _semaphore = threading.Semaphore(GIGACHAT_MAX_RPS)
    _call_counter = 0
    _error_counter = 0
    _lock = threading.Lock()

    def generate(self, context: str, dialog_messages: list[dict]) -> PatientResponse:
        acquired = self._semaphore.acquire(timeout=5.0)
        if not acquired:
            # Rate-limit exceeded — имитируем поведение GigaChat при перегрузке
            with self._lock:
                RealisticFakeLLM._error_counter += 1
            raise RuntimeError("GigaChat rate limit exceeded")

        try:
            with self._lock:
                RealisticFakeLLM._call_counter += 1

            # Имитируем задержку сети + обработки
            jitter = random.uniform(0, 0.1)
            time.sleep(GIGACHAT_MOCK_DELAY_MS / 1000 + jitter)

            # Имитируем случайные ошибки
            if random.random() < GIGACHAT_ERROR_RATE:
                with self._lock:
                    RealisticFakeLLM._error_counter += 1
                raise ConnectionError("GigaChat temporary error")

            return PatientResponse(
                text="Да, у меня болит живот уже второй день.",
                complaints=["боль в животе"],
                anamnesis=["симптомы 2 дня"],
                diagnostics=[],
            )
        finally:
            self._semaphore.release()

    @classmethod
    def reset_counters(cls):
        with cls._lock:
            cls._call_counter = 0
            cls._error_counter = 0


# ─────────────────────────────────────────────────────────────────────────────
# Result collection
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class UserResult:
    user_id: int
    turns_completed: int
    total_time_s: float
    turn_times_ms: List[float]
    errors: List[str] = field(default_factory=list)
    diagnosis_correct: Optional[bool] = None


# ─────────────────────────────────────────────────────────────────────────────
# User simulation
# ─────────────────────────────────────────────────────────────────────────────

DOCTOR_QUESTIONS = [
    "Здравствуйте, на что жалуетесь?",
    "Как давно это началось?",
    "Где именно болит?",
    "Была ли температура?",
    "Есть ли тошнота или рвота?",
    "Принимали ли лекарства?",
    "Как боль меняется при движении?",
    "Были ли подобные симптомы раньше?",
]

DIAGNOSES = {
    DiseaseType.APPENDICITIS: "аппендицит",
    DiseaseType.DIABETES:     "диабет",
    DiseaseType.ANEMIA:       "анемия",
    DiseaseType.TUBERCULOSIS: "туберкулез",
    DiseaseType.EPILEPSY:     "эпилепсия",
}


def simulate_user(user_id: int, llm_class, barrier: threading.Barrier) -> UserResult:
    disease_type = random.choice(list(DiseaseType))
    patient = create_patient(disease_type)
    card = MedicalCard()
    llm = llm_class()
    engine = DialogEngine(patient=patient, card=card, llm=llm)

    check_uc = CheckDiagnosisUseCase()
    turn_times = []
    errors = []

    # Ждём старта всех потоков одновременно
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
            elapsed_ms = (time.perf_counter() - t0) * 1000
            turn_times.append(elapsed_ms)

    # Финальный шаг: выставить диагноз
    user_diag = DIAGNOSES[disease_type]
    try:
        result = check_uc.execute(user_diag, patient, card)
        diagnosis_correct = result.is_correct
    except Exception as e:
        errors.append(f"diagnosis: {e}")
        diagnosis_correct = None

    total_time = time.perf_counter() - start_total

    return UserResult(
        user_id=user_id,
        turns_completed=TURNS_PER_USER - len([e for e in errors if e.startswith("turn")]),
        total_time_s=total_time,
        turn_times_ms=turn_times,
        errors=errors,
        diagnosis_correct=diagnosis_correct,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test runners
# ─────────────────────────────────────────────────────────────────────────────

def run_concurrent_users(n_users: int, llm_class, label: str) -> dict:
    barrier = threading.Barrier(n_users)
    results: List[Optional[UserResult]] = [None] * n_users
    threads = []

    def worker(i):
        results[i] = simulate_user(i, llm_class, barrier)

    for i in range(n_users):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)

    wall_start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall_time = time.perf_counter() - wall_start

    all_turn_times = []
    total_errors = 0
    correct_diagnoses = 0
    diagnosis_attempts = 0

    for r in results:
        if r is None:
            continue
        all_turn_times.extend(r.turn_times_ms)
        total_errors += len(r.errors)
        if r.diagnosis_correct is not None:
            diagnosis_attempts += 1
            if r.diagnosis_correct:
                correct_diagnoses += 1

    total_turns = n_users * TURNS_PER_USER
    throughput = total_turns / wall_time

    return {
        "label": label,
        "n_users": n_users,
        "wall_time_s": round(wall_time, 3),
        "total_turns": total_turns,
        "throughput_turns_per_sec": round(throughput, 2),
        "latency_p50_ms": round(statistics.median(all_turn_times), 1) if all_turn_times else 0,
        "latency_p95_ms": round(sorted(all_turn_times)[int(len(all_turn_times) * 0.95)], 1) if all_turn_times else 0,
        "latency_p99_ms": round(sorted(all_turn_times)[int(len(all_turn_times) * 0.99)], 1) if all_turn_times else 0,
        "latency_max_ms": round(max(all_turn_times), 1) if all_turn_times else 0,
        "latency_mean_ms": round(statistics.mean(all_turn_times), 1) if all_turn_times else 0,
        "total_errors": total_errors,
        "error_rate_pct": round(total_errors / total_turns * 100, 2),
        "diagnosis_accuracy_pct": round(correct_diagnoses / diagnosis_attempts * 100, 1) if diagnosis_attempts else 0,
    }


def run_gigachat_rate_limit_test() -> List[dict]:
    """Тестирует предельную нагрузку на GigaChat при разном кол-ве пользователей."""
    results = []
    for n in RATE_LIMIT_USER_COUNTS:
        RealisticFakeLLM.reset_counters()
        result = run_concurrent_users(n, lambda: RealisticFakeLLM(), f"GigaChat {n} users")
        result["gigachat_total_calls"] = RealisticFakeLLM._call_counter
        result["gigachat_errors"] = RealisticFakeLLM._error_counter
        result["gigachat_error_rate_pct"] = round(
            RealisticFakeLLM._error_counter / max(RealisticFakeLLM._call_counter + RealisticFakeLLM._error_counter, 1) * 100, 1
        )
        results.append(result)
        print(f"  [{n:3d} users] wall={result['wall_time_s']:.2f}s "
              f"p50={result['latency_p50_ms']}ms "
              f"p95={result['latency_p95_ms']}ms "
              f"errors={result['total_errors']} "
              f"giga_errors={RealisticFakeLLM._error_counter}")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Report generation
# ─────────────────────────────────────────────────────────────────────────────

def format_report(instant_result: dict, realistic_result: dict, rate_limit_results: List[dict]) -> str:
    lines = []
    sep = "=" * 70

    lines.append(sep)
    lines.append("  НАГРУЗОЧНЫЙ ТЕСТ — СИМУЛЯТОР ПАЦИЕНТОВ ДЛЯ ВРАЧЕЙ")
    lines.append(sep)
    lines.append(f"  Конфигурация:")
    lines.append(f"    Одновременных пользователей : {CONCURRENT_USERS}")
    lines.append(f"    Ходов диалога на пользователя: {TURNS_PER_USER}")
    lines.append(f"    Имит. ограничение GigaChat   : {GIGACHAT_MAX_RPS} потока")
    lines.append(f"    Имит. задержка GigaChat      : {GIGACHAT_MOCK_DELAY_MS} ms")
    lines.append(f"    Имит. частота ошибок         : {GIGACHAT_ERROR_RATE*100:.0f}%")
    lines.append("")

    def fmt_result(r: dict):
        lines.append(f"  Сценарий : {r['label']}")
        lines.append(f"  Пользователей  : {r['n_users']}")
        lines.append(f"  Общее время    : {r['wall_time_s']} с")
        lines.append(f"  Всего ходов    : {r['total_turns']}")
        lines.append(f"  Пропускная способность: {r['throughput_turns_per_sec']} ходов/сек")
        lines.append(f"  Задержка (ms):")
        lines.append(f"    Среднее : {r['latency_mean_ms']}")
        lines.append(f"    P50     : {r['latency_p50_ms']}")
        lines.append(f"    P95     : {r['latency_p95_ms']}")
        lines.append(f"    P99     : {r['latency_p99_ms']}")
        lines.append(f"    Макс.   : {r['latency_max_ms']}")
        lines.append(f"  Ошибок    : {r['total_errors']} ({r['error_rate_pct']}%)")
        lines.append(f"  Точность диагнозов: {r['diagnosis_accuracy_pct']}%")
        if "gigachat_errors" in r:
            lines.append(f"  GigaChat вызовов  : {r.get('gigachat_total_calls', '?')}")
            lines.append(f"  GigaChat ошибок   : {r.get('gigachat_errors', '?')} ({r.get('gigachat_error_rate_pct', '?')}%)")
        lines.append("")

    lines.append(sep)
    lines.append("  ТЕСТ 1: Бизнес-логика (мгновенный LLM, без задержек)")
    lines.append(sep)
    fmt_result(instant_result)

    lines.append(sep)
    lines.append("  ТЕСТ 2: Реалистичный сценарий (имитация GigaChat, 50 юзеров)")
    lines.append(sep)
    fmt_result(realistic_result)

    lines.append(sep)
    lines.append("  ТЕСТ 3: Предельная нагрузка GigaChat при разном кол-ве пользователей")
    lines.append(f"          (rate-limit = {GIGACHAT_MAX_RPS} потока, задержка = {GIGACHAT_MOCK_DELAY_MS}ms)")
    lines.append(sep)
    lines.append(f"  {'Users':>6} | {'wall(s)':>8} | {'p50(ms)':>8} | {'p95(ms)':>8} | "
                 f"{'errors':>7} | {'giga_err':>9} | {'throughput':>11}")
    lines.append("  " + "-" * 68)
    for r in rate_limit_results:
        lines.append(
            f"  {r['n_users']:>6} | "
            f"{r['wall_time_s']:>8.2f} | "
            f"{r['latency_p50_ms']:>8.1f} | "
            f"{r['latency_p95_ms']:>8.1f} | "
            f"{r['total_errors']:>7} | "
            f"{r.get('gigachat_errors', 0):>9} | "
            f"{r['throughput_turns_per_sec']:>10.2f}x"
        )

    lines.append("")
    lines.append(sep)
    lines.append("  АНАЛИЗ ПРЕДЕЛЬНОЙ НАГРУЗКИ НА GIGACHAT")
    lines.append(sep)

    # Найти точку деградации
    prev = None
    degradation_point = None
    for r in rate_limit_results:
        if prev and r.get("gigachat_errors", 0) > prev.get("gigachat_errors", 0) * 2:
            degradation_point = r["n_users"]
            break
        prev = r

    first_error_at = None
    for r in rate_limit_results:
        if r.get("gigachat_errors", 0) > 0:
            first_error_at = r["n_users"]
            break

    lines.append(f"  Первые ошибки GigaChat при : {first_error_at} пользователях")
    if degradation_point:
        lines.append(f"  Точка деградации           : {degradation_point} пользователей")
    else:
        lines.append(f"  Точка деградации           : в пределах теста не достигнута")

    # Находим максимальный throughput
    max_tp = max(rate_limit_results, key=lambda r: r["throughput_turns_per_sec"])
    lines.append(f"  Пиковая пропускная способность: {max_tp['throughput_turns_per_sec']} ходов/сек "
                 f"при {max_tp['n_users']} пользователях")


    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 70)
    print("  НАГРУЗОЧНЫЙ ТЕСТ — СИМУЛЯТОР ПАЦИЕНТОВ ДЛЯ ВРАЧЕЙ")
    print("=" * 70)

    print(f"\n[1/3] Тест бизнес-логики: {CONCURRENT_USERS} пользователей, мгновенный LLM...")
    instant_result = run_concurrent_users(
        CONCURRENT_USERS,
        lambda: InstantFakeLLM(),
        f"InstantLLM {CONCURRENT_USERS} users",
    )
    print(f"      ✓ wall={instant_result['wall_time_s']}s "
          f"p50={instant_result['latency_p50_ms']}ms "
          f"throughput={instant_result['throughput_turns_per_sec']}t/s "
          f"errors={instant_result['total_errors']}")

    print(f"\n[2/3] Реалистичный тест: {CONCURRENT_USERS} пользователей, GigaChat imitation...")
    RealisticFakeLLM.reset_counters()
    realistic_result = run_concurrent_users(
        CONCURRENT_USERS,
        lambda: RealisticFakeLLM(),
        f"RealisticGigaChat {CONCURRENT_USERS} users",
    )
    realistic_result["gigachat_total_calls"] = RealisticFakeLLM._call_counter
    realistic_result["gigachat_errors"] = RealisticFakeLLM._error_counter
    realistic_result["gigachat_error_rate_pct"] = round(
        RealisticFakeLLM._error_counter / max(RealisticFakeLLM._call_counter + RealisticFakeLLM._error_counter, 1) * 100, 1
    )
    print(f"      ✓ wall={realistic_result['wall_time_s']}s "
          f"p50={realistic_result['latency_p50_ms']}ms "
          f"p95={realistic_result['latency_p95_ms']}ms "
          f"giga_errors={RealisticFakeLLM._error_counter}")

    print(f"\n[3/3] Предельная нагрузка GigaChat ({RATE_LIMIT_USER_COUNTS})...")
    rate_limit_results = run_gigachat_rate_limit_test()

    report = format_report(instant_result, realistic_result, rate_limit_results)

    print("\n" + report)

    # Сохраняем отчёт
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "load_test_report.txt")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  Отчёт сохранён: {report_path}")


if __name__ == "__main__":
    main()