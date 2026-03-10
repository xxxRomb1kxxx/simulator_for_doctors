#!/usr/bin/env python3
"""
Запускает все unit-тесты и формирует итоговый отчёт.
Использует только stdlib — pytest не требуется.

Запуск из корня проекта: python test/run_tests.py
"""
import sys
import os
import unittest
import time
import io

# Корень проекта — папка выше test/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR     = os.path.dirname(os.path.abspath(__file__))

# Добавляем корень проекта в путь поиска модулей
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# Добавляем папку test/ (нужно для прямого импорта test_*)
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

# ─── Моки внешних зависимостей (до импорта тестов) ───────────────────────────
from unittest.mock import MagicMock

# aiogram
aiogram_mock = MagicMock()
sys.modules["aiogram"] = aiogram_mock
sys.modules["aiogram.fsm"] = aiogram_mock
sys.modules["aiogram.fsm.state"] = aiogram_mock

# langchain_gigachat
sys.modules["langchain_gigachat"] = MagicMock()

# langchain_core.messages — реальные классы-заглушки для isinstance-проверок
class FakeSystemMessage:
    def __init__(self, content): self.content = content

class FakeHumanMessage:
    def __init__(self, content): self.content = content

class FakeAIMessage:
    def __init__(self, content): self.content = content

lc_core_mock = MagicMock()
lc_core_mock.messages.SystemMessage = FakeSystemMessage
lc_core_mock.messages.HumanMessage  = FakeHumanMessage
lc_core_mock.messages.AIMessage     = FakeAIMessage
lc_core_mock.messages.BaseMessage   = object
sys.modules["langchain_core"]          = lc_core_mock
sys.modules["langchain_core.messages"] = lc_core_mock.messages

# pydantic_settings
ps_mock = MagicMock()
class FakeBaseSettings:
    def __init__(self, **kw): pass
ps_mock.BaseSettings       = FakeBaseSettings
ps_mock.SettingsConfigDict = dict
sys.modules["pydantic_settings"] = ps_mock

# pydantic
pydantic_mock = MagicMock()
pydantic_mock.Field           = lambda *a, **kw: None
pydantic_mock.field_validator = lambda *a, **kw: (lambda f: f)
sys.modules["pydantic"] = pydantic_mock

# tenacity — убираем retry, чтобы ошибки всплывали сразу
tenacity_mock = MagicMock()
def _fake_retry(*a, **kw):
    def dec(f): return f
    return dec
tenacity_mock.retry                   = _fake_retry
tenacity_mock.stop_after_attempt      = MagicMock(return_value=None)
tenacity_mock.wait_exponential        = MagicMock(return_value=None)
tenacity_mock.retry_if_exception_type = MagicMock(return_value=None)
sys.modules["tenacity"] = tenacity_mock

# config / redis
sys.modules["config"] = MagicMock()
sys.modules["redis"]  = MagicMock()

# ─── Список тестовых модулей ──────────────────────────────────────────────────
# Используем прямые имена файлов (без "test." префикса),
# т.к. TEST_DIR уже в sys.path
SUITE_MODULES = [
    ("test_models",                 "Модели (MedicalCard, Patient, Disease)"),
    ("test_diagnosis",              "Сервис диагностики (check, similarity)"),
    ("test_patient_factory",        "Фабрика пациентов и реестр болезней"),
    ("test_dialog_engine",          "DialogEngine (с мок-LLM)"),
    ("test_case_service",           "CaseService (Use Cases)"),
    ("test_llm_response_generator", "LLM генератор (parse, fallback)"),
]


def run_suite(module_name: str) -> tuple:
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromName(module_name)
    buf    = io.StringIO()
    runner = unittest.TextTestRunner(stream=buf, verbosity=2)
    result = runner.run(suite)
    return result, buf.getvalue()


def main() -> int:
    print("\n" + "=" * 70)
    print("  UNIT-ТЕСТЫ — СИМУЛЯТОР ПАЦИЕНТОВ ДЛЯ ВРАЧЕЙ")
    print("=" * 70)

    total_run = total_errors = total_failures = 0
    all_output: list = []
    suite_results: list = []
    start = time.perf_counter()

    for module_name, label in SUITE_MODULES:
        t0 = time.perf_counter()
        result, output = run_suite(module_name)
        elapsed = time.perf_counter() - t0

        run      = result.testsRun
        errors   = len(result.errors)
        failures = len(result.failures)
        passed   = run - errors - failures
        status   = "✓ PASS" if (errors + failures) == 0 else "✗ FAIL"

        total_run      += run
        total_errors   += errors
        total_failures += failures
        all_output.append(f"\n{'=' * 70}\n  {label}\n{'=' * 70}\n{output}")
        suite_results.append(dict(label=label, run=run, passed=passed,
                                  failures=failures, errors=errors,
                                  elapsed=elapsed, status=status))

        print(f"  {status}  {label}")
        print(f"          {passed}/{run} тестов прошло за {elapsed:.3f}с", end="")
        if failures: print(f"  ← {failures} failures", end="")
        if errors:   print(f"  ← {errors} errors",     end="")
        print()

    total_elapsed = time.perf_counter() - start
    total_passed  = total_run - total_errors - total_failures

    print()
    print("=" * 70)
    print(f"  ИТОГО: {total_passed}/{total_run} прошло | "
          f"{total_failures} failures | {total_errors} errors | "
          f"{total_elapsed:.3f}с")
    print("=" * 70)

    if total_failures + total_errors > 0:
        print("\n  ДЕТАЛИ ОШИБОК:")
        print("\n".join(all_output))

    report_dir = os.path.join(TEST_DIR, "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "unit_test_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("UNIT-ТЕСТЫ — СИМУЛЯТОР ПАЦИЕНТОВ ДЛЯ ВРАЧЕЙ\n")
        f.write("=" * 70 + "\n\n")
        for sr in suite_results:
            f.write(f"{sr['status']}  {sr['label']}\n")
            f.write(f"  {sr['passed']}/{sr['run']} passed | "
                    f"failures={sr['failures']} | errors={sr['errors']} | "
                    f"time={sr['elapsed']:.3f}s\n\n")
        f.write("=" * 70 + "\n")
        f.write(f"TOTAL: {total_passed}/{total_run} passed | "
                f"failures={total_failures} | errors={total_errors} | "
                f"time={total_elapsed:.3f}s\n")
        f.write("=" * 70 + "\n\n")
        f.write("ДЕТАЛЬНЫЙ ВЫВОД\n")
        f.write("\n".join(all_output))

    print(f"\n  Отчёт сохранён: {report_path}")
    return 0 if (total_failures + total_errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())