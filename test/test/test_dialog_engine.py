import unittest
from unittest.mock import MagicMock

from models.models import Disease, DiseaseType, MedicalCard, Patient
from giga.llm_response_generator import IResponseGenerator, PatientResponse
from dialog_engine.dialog_engine import DialogEngine


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_response(
    text="Ответ пациента",
    complaints=None,
    anamnesis=None,
    diagnostics=None,
) -> PatientResponse:
    return PatientResponse(
        text=text,
        complaints=complaints or [],
        anamnesis=anamnesis or [],
        diagnostics=diagnostics or [],
    )


class FakeLLM(IResponseGenerator):
    """Детерминированный заменитель GigaChat."""

    def __init__(self, response: PatientResponse | None = None):
        self._response = response or _make_response()
        self.calls: list[dict] = []

    def generate(self, context: str, dialog_messages: list[dict]) -> PatientResponse:
        self.calls.append({"context": context, "messages": dialog_messages})
        return self._response


def _make_patient(disease_type: DiseaseType = DiseaseType.APPENDICITIS) -> Patient:
    from models.patient_factory import create_patient
    return create_patient(disease_type)


def _make_engine(response: PatientResponse | None = None) -> tuple[DialogEngine, FakeLLM]:
    patient = _make_patient()
    card = MedicalCard()
    llm = FakeLLM(response)
    engine = DialogEngine(patient=patient, card=card, llm=llm)
    return engine, llm


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDialogEngineProcess(unittest.TestCase):

    def test_process_returns_llm_text(self):
        engine, _ = _make_engine(_make_response(text="Болит живот"))
        result = engine.process("Как вы себя чувствуете?")
        self.assertEqual(result, "Болит живот")

    def test_process_calls_llm_once(self):
        engine, llm = _make_engine()
        engine.process("Привет")
        self.assertEqual(len(llm.calls), 1)

    def test_process_passes_user_text_to_history(self):
        engine, llm = _make_engine()
        engine.process("Что вас беспокоит?")
        messages = llm.calls[0]["messages"]
        user_msgs = [m for m in messages if m["role"] == "user"]
        contents = [m["content"] for m in user_msgs]
        self.assertIn("Что вас беспокоит?", contents)

    def test_first_process_stage_is_greeting(self):
        """Первый вызов process() должен добавлять «начало приёма» в контекст."""
        engine, llm = _make_engine()
        engine.process("Здравствуйте")
        context = llm.calls[0]["context"]
        self.assertIn("начало приёма", context.lower())

    def test_second_process_no_greeting_extra(self):
        """Второй и последующие вызовы не должны содержать «начало приёма»."""
        engine, llm = _make_engine()
        engine.process("Первый вопрос")
        engine.process("Второй вопрос")
        context_second = llm.calls[1]["context"]
        self.assertNotIn("начало приёма", context_second.lower())

    def test_process_appends_assistant_to_history(self):
        resp = _make_response(text="Ответ пациента 42")
        engine, llm = _make_engine(resp)
        engine.process("Вопрос")
        # Второй вызов — история должна содержать предыдущий ответ
        engine.process("Второй вопрос")
        messages_2 = llm.calls[1]["messages"]
        assistant_msgs = [m for m in messages_2 if m["role"] == "assistant"]
        self.assertTrue(any("Ответ пациента 42" in m["content"] for m in assistant_msgs))

    def test_process_history_limited_to_20(self):
        engine, llm = _make_engine()
        for i in range(25):
            engine.process(f"Вопрос {i}")
        last_call_messages = llm.calls[-1]["messages"]
        self.assertLessEqual(len(last_call_messages), 20)

    def test_multiple_process_calls_work(self):
        engine, llm = _make_engine()
        for i in range(10):
            result = engine.process(f"Вопрос {i}")
            self.assertIsInstance(result, str)
        self.assertEqual(len(llm.calls), 10)


class TestDialogEngineMedicalCard(unittest.TestCase):

    def test_complaints_merged_into_card(self):
        resp = _make_response(complaints=["боль в правом боку", "тошнота"])
        engine, _ = _make_engine(resp)
        engine.process("Что болит?")
        self.assertIn("боль в правом боку", engine.card.complaints)
        self.assertIn("тошнота", engine.card.complaints)

    def test_anamnesis_merged_into_card(self):
        resp = _make_response(anamnesis=["симптомы 6 часов"])
        engine, _ = _make_engine(resp)
        engine.process("Когда началось?")
        self.assertIn("симптомы 6 часов", engine.card.anamnesis)

    def test_diagnostics_merged_into_card(self):
        resp = _make_response(diagnostics=["узи выявило патологию"])
        engine, _ = _make_engine(resp)
        engine.process("Делали ли УЗИ?")
        self.assertIn("узи выявило патологию", engine.card.diagnostics)

    def test_duplicate_complaints_not_added_twice(self):
        resp = _make_response(complaints=["Боль в животе"])
        engine, _ = _make_engine(resp)
        engine.process("Первый вопрос")
        engine.process("Второй вопрос")
        count = engine.card.complaints.count("Боль в животе")
        self.assertEqual(count, 1)

    def test_card_accumulates_across_turns(self):
        engine, llm = _make_engine()

        llm._response = _make_response(complaints=["жалоба 1"])
        engine.process("Вопрос 1")

        llm._response = _make_response(complaints=["жалоба 2"])
        engine.process("Вопрос 2")

        self.assertIn("жалоба 1", engine.card.complaints)
        self.assertIn("жалоба 2", engine.card.complaints)

    def test_empty_response_does_not_break_card(self):
        resp = _make_response(complaints=[], anamnesis=[], diagnostics=[])
        engine, _ = _make_engine(resp)
        engine.process("Вопрос")
        # Карта должна оставаться пустой
        self.assertEqual(engine.card.complaints, [])

    def test_card_is_shared_with_caller(self):
        patient = _make_patient()
        card = MedicalCard()
        llm = FakeLLM(_make_response(complaints=["жалоба"]))
        engine = DialogEngine(patient=patient, card=card, llm=llm)
        engine.process("Вопрос")
        # card и engine.card — один объект
        self.assertIs(engine.card, card)
        self.assertIn("жалоба", card.complaints)


class TestDialogEngineReset(unittest.TestCase):

    def test_reset_clears_history(self):
        engine, llm = _make_engine()
        engine.process("Вопрос перед сбросом")
        engine.reset()
        # После reset — первый вызов снова greeting
        engine.process("Вопрос после сброса")
        context = llm.calls[-1]["context"]
        self.assertIn("начало приёма", context.lower())

    def test_reset_allows_reuse(self):
        engine, llm = _make_engine()
        for _ in range(3):
            engine.reset()
            engine.process("Вопрос")
        self.assertEqual(len(llm.calls), 3)


class TestDialogEngineContext(unittest.TestCase):

    def test_context_contains_disease_info(self):
        engine, llm = _make_engine()
        engine.process("Вопрос")
        context = llm.calls[0]["context"]
        # Контекст должен содержать название болезни пациента
        self.assertIn(engine.patient.disease.name, context)

    def test_context_contains_age(self):
        engine, llm = _make_engine()
        engine.process("Вопрос")
        context = llm.calls[0]["context"]
        self.assertIn(str(engine.patient.age), context)

    def test_context_contains_gender(self):
        engine, llm = _make_engine()
        engine.process("Вопрос")
        context = llm.calls[0]["context"]
        self.assertIn(engine.patient.gender, context)

    def test_context_contains_accumulated_complaints(self):
        resp = _make_response(complaints=["боль в животе"])
        engine, llm = _make_engine(resp)
        engine.process("Вопрос 1")
        # Второй вопрос — в контексте должны быть уже собранные жалобы
        engine.process("Вопрос 2")
        context_second = llm.calls[1]["context"]
        self.assertIn("боль в животе", context_second.lower())


class TestDialogEngineFallback(unittest.TestCase):
    """Проверяем, что движок корректно обрабатывает исключения от LLM."""

    def test_llm_exception_raises_to_caller(self):
        """Исключение из LLM должно подняться в caller (fallback на уровне GigachatResponseGenerator, не DialogEngine)."""
        class FailingLLM(IResponseGenerator):
            def generate(self, context, dialog_messages):
                raise RuntimeError("LLM недоступен")

        patient = _make_patient()
        card = MedicalCard()
        engine = DialogEngine(patient=patient, card=card, llm=FailingLLM())
        with self.assertRaises(RuntimeError):
            engine.process("Вопрос")


if __name__ == "__main__":
    unittest.main(verbosity=2)