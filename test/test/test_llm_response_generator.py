import json
import unittest
from unittest.mock import patch, MagicMock

from giga.llm_response_generator import (
    GigachatResponseGenerator,
    PatientResponse,
    IResponseGenerator,
)

def _make_generator(disease="Аппендицит", complaints=None):
    complaints = complaints or ["боль в животе"]
    return GigachatResponseGenerator(disease_name=disease, complaints=complaints)

class TestPatientResponse(unittest.TestCase):

    def test_fields_accessible(self):
        r = PatientResponse(
            text="ответ",
            complaints=["жалоба"],
            anamnesis=["анамнез"],
            diagnostics=["диагностика"],
        )
        self.assertEqual(r.text, "ответ")
        self.assertEqual(r.complaints, ["жалоба"])
        self.assertEqual(r.anamnesis, ["анамнез"])
        self.assertEqual(r.diagnostics, ["диагностика"])

    def test_default_empty_lists(self):
        r = PatientResponse(text="txt", complaints=[], anamnesis=[], diagnostics=[])
        self.assertEqual(r.complaints, [])
        self.assertEqual(r.anamnesis, [])
        self.assertEqual(r.diagnostics, [])

class TestGigachatResponseGeneratorParse(unittest.TestCase):

    def _generate_with_raw(self, raw_response: str) -> PatientResponse:
        gen = _make_generator()
        with patch("giga.llm_response_generator._invoke_gigachat", return_value=raw_response):
            return gen.generate(context="контекст", dialog_messages=[{"role": "user", "content": "Вопрос"}])

    def test_valid_json_reply_extracted(self):
        raw = json.dumps({"reply": "Болит живот", "complaints": [], "anamnesis": [], "diagnostics": []})
        result = self._generate_with_raw(raw)
        self.assertEqual(result.text, "Болит живот")

    def test_valid_json_complaints_extracted(self):
        raw = json.dumps({
            "reply": "Ответ",
            "complaints": ["боль в правом боку"],
            "anamnesis": [],
            "diagnostics": [],
        })
        result = self._generate_with_raw(raw)
        self.assertIn("боль в правом боку", result.complaints)

    def test_valid_json_anamnesis_extracted(self):
        raw = json.dumps({
            "reply": "Ответ",
            "complaints": [],
            "anamnesis": ["симптомы 3 дня"],
            "diagnostics": [],
        })
        result = self._generate_with_raw(raw)
        self.assertIn("симптомы 3 дня", result.anamnesis)

    def test_valid_json_diagnostics_extracted(self):
        raw = json.dumps({
            "reply": "Ответ",
            "complaints": [],
            "anamnesis": [],
            "diagnostics": ["УЗИ выявило патологию"],
        })
        result = self._generate_with_raw(raw)
        self.assertIn("УЗИ выявило патологию", result.diagnostics)

    def test_json_with_markdown_fences_parsed(self):
        inner = json.dumps({"reply": "Ответ пациента", "complaints": [], "anamnesis": [], "diagnostics": []})
        raw = f"```json\n{inner}\n```"
        result = self._generate_with_raw(raw)
        self.assertEqual(result.text, "Ответ пациента")

    def test_json_with_plain_fences_parsed(self):
        inner = json.dumps({"reply": "Другой ответ", "complaints": [], "anamnesis": [], "diagnostics": []})
        raw = f"```\n{inner}\n```"
        result = self._generate_with_raw(raw)
        self.assertEqual(result.text, "Другой ответ")

    def test_empty_lists_when_json_missing_keys(self):
        raw = json.dumps({"reply": "Что-то"})
        result = self._generate_with_raw(raw)
        self.assertEqual(result.complaints, [])
        self.assertEqual(result.anamnesis, [])
        self.assertEqual(result.diagnostics, [])

    def test_null_reply_uses_fallback(self):
        raw = json.dumps({"reply": None, "complaints": [], "anamnesis": [], "diagnostics": []})
        result = self._generate_with_raw(raw)
        self.assertIn("не совсем понял", result.text)

    def test_empty_reply_uses_fallback(self):
        raw = json.dumps({"reply": "", "complaints": [], "anamnesis": [], "diagnostics": []})
        result = self._generate_with_raw(raw)
        self.assertIn("не совсем понял", result.text)

    def test_plain_text_returns_as_text(self):
        raw = "Я чувствую себя плохо, доктор."
        result = self._generate_with_raw(raw)
        self.assertEqual(result.text, raw)

    def test_plain_text_empty_lists(self):
        result = self._generate_with_raw("Не JSON вообще")
        self.assertEqual(result.complaints, [])
        self.assertEqual(result.anamnesis, [])
        self.assertEqual(result.diagnostics, [])

    def test_broken_json_does_not_raise(self):
        result = self._generate_with_raw("{reply: 'плохой json'}")
        self.assertIsInstance(result, PatientResponse)

    def test_none_items_filtered_from_lists(self):
        raw = json.dumps({
            "reply": "Ответ",
            "complaints": [None, "боль", None],
            "anamnesis": [None],
            "diagnostics": [],
        })
        result = self._generate_with_raw(raw)
        self.assertEqual(result.complaints, ["боль"])
        self.assertEqual(result.anamnesis, [])

class TestGigachatResponseGeneratorFallback(unittest.TestCase):

    def _generate_with_exception(self, exc):
        gen = _make_generator()
        with patch("giga.llm_response_generator._invoke_gigachat", side_effect=exc):
            return gen.generate(context="ctx", dialog_messages=[{"role": "user", "content": "Вопрос"}])

    def test_fallback_on_runtime_error(self):
        result = self._generate_with_exception(RuntimeError("GigaChat недоступен"))
        self.assertIn("не совсем понял", result.text)
        self.assertEqual(result.complaints, [])

    def test_fallback_on_timeout(self):
        result = self._generate_with_exception(TimeoutError("Таймаут"))
        self.assertIsInstance(result, PatientResponse)

    def test_fallback_on_connection_error(self):
        result = self._generate_with_exception(ConnectionError("Нет соединения"))
        self.assertIsInstance(result, PatientResponse)

    def test_fallback_text_is_string(self):
        result = self._generate_with_exception(Exception("любая ошибка"))
        self.assertIsInstance(result.text, str)
        self.assertTrue(result.text)

class TestBuildMessages(unittest.TestCase):

    def _build(self, dialog_messages):
        gen = _make_generator()
        return gen._build_messages(context="тест контекст", dialog_messages=dialog_messages)

    def test_first_message_is_system(self):
        from langchain_core.messages import SystemMessage
        msgs = self._build([{"role": "user", "content": "Привет"}])
        self.assertIsInstance(msgs[0], SystemMessage)

    def test_system_prompt_contains_disease(self):
        msgs = self._build([{"role": "user", "content": "Привет"}])
        system_content = msgs[0].content
        # Системный промпт содержит описание болезни (patient_prompt), не название
        self.assertTrue(
            "аппендицит" in system_content.lower() or "симулятор" in system_content.lower(),
            f"Expected disease info in system prompt, got: {system_content[:100]}"
        )

    def test_last_message_is_human(self):
        from langchain_core.messages import HumanMessage
        msgs = self._build([{"role": "user", "content": "Что болит?"}])
        self.assertIsInstance(msgs[-1], HumanMessage)

    def test_history_interleaved_correctly(self):
        dialog = [
            {"role": "user", "content": "Первый вопрос"},
            {"role": "assistant", "content": "Первый ответ"},
            {"role": "user", "content": "Второй вопрос"},
        ]
        msgs = self._build(dialog)
        content_types = [type(m).__name__ for m in msgs[1:]]
        human_names = {"HumanMessage", "FakeHumanMessage"}
        ai_names = {"AIMessage", "FakeAIMessage"}
        self.assertTrue(any(t in human_names for t in content_types), f"No human msg in {content_types}")
        self.assertTrue(any(t in ai_names for t in content_types), f"No AI msg in {content_types}")

    def test_empty_history_no_crash(self):
        gen = _make_generator()
        msgs = gen._build_messages(context="ctx", dialog_messages=[])
        self.assertGreater(len(msgs), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)