import unittest
from unittest.mock import patch, MagicMock

from models.models import DiseaseType, MedicalCard
from models.patient_factory import create_patient
from services.case_service import (
    CaseRepository,
    StartCaseUseCase,
    CheckDiagnosisUseCase,
    ProcessDialogUseCase,
    start_random_case,
    start_case_by_type,
    check_diagnosis,
    process_dialog,
    CaseInitResult,
    DiagnosisResult,
)
from dialog_engine.dialog_engine import DialogEngine
from giga.llm_response_generator import IResponseGenerator, PatientResponse


class FakeLLM(IResponseGenerator):
    def generate(self, context, dialog_messages):
        return PatientResponse(text="ответ", complaints=[], anamnesis=[], diagnostics=[])


class TestCaseRepository(unittest.TestCase):

    def _build_with_fake_llm(self, disease_type):
        """CaseRepository.build создаёт реальный DialogEngine с GigaChat.
        Мы патчим DialogEngine.__init__ чтобы не дёргать сеть."""
        with patch("services.case_service.DialogEngine") as MockEngine:
            MockEngine.return_value = MagicMock()
            result = CaseRepository.build(disease_type)
        return result

    def test_build_returns_case_init_result(self):
        result = self._build_with_fake_llm(DiseaseType.APPENDICITIS)
        self.assertIsInstance(result, CaseInitResult)

    def test_build_creates_patient(self):
        result = self._build_with_fake_llm(DiseaseType.DIABETES)
        self.assertIsNotNone(result.patient)
        self.assertEqual(result.patient.disease.name, "Сахарный диабет")

    def test_build_creates_empty_card(self):
        result = self._build_with_fake_llm(DiseaseType.ANEMIA)
        self.assertIsInstance(result.card, MedicalCard)
        self.assertEqual(result.card.complaints, [])

    def test_build_random_returns_valid_result(self):
        result = self._build_with_fake_llm(DiseaseType.EPILEPSY)
        self.assertIsNotNone(result.patient)
        self.assertIsNotNone(result.card)

    def test_all_disease_types_buildable(self):
        for dt in DiseaseType:
            result = self._build_with_fake_llm(dt)
            self.assertIsNotNone(result)


class TestStartCaseUseCase(unittest.TestCase):

    def setUp(self):
        self.patcher = patch("services.case_service.DialogEngine")
        self.MockEngine = self.patcher.start()
        self.MockEngine.return_value = MagicMock()

    def tearDown(self):
        self.patcher.stop()

    def test_by_type_appendicitis(self):
        uc = StartCaseUseCase(CaseRepository())
        result = uc.by_type(DiseaseType.APPENDICITIS)
        self.assertEqual(result.patient.disease.name, "Аппендицит")

    def test_by_type_returns_correct_disease_type(self):
        uc = StartCaseUseCase(CaseRepository())
        for dt in DiseaseType:
            result = uc.by_type(dt)
            self.assertIsNotNone(result.patient)

    def test_random_returns_result(self):
        uc = StartCaseUseCase(CaseRepository())
        result = uc.random()
        self.assertIsNotNone(result.patient)
        self.assertIsNotNone(result.card)


class TestProcessDialogUseCase(unittest.TestCase):

    def _make_engine(self):
        patient = create_patient(DiseaseType.APPENDICITIS)
        card = MedicalCard()
        return DialogEngine(patient=patient, card=card, llm=FakeLLM())

    def test_execute_returns_string(self):
        uc = ProcessDialogUseCase()
        engine = self._make_engine()
        result = uc.execute(engine, "Что болит?")
        self.assertIsInstance(result, str)

    def test_execute_passes_text_to_engine(self):
        uc = ProcessDialogUseCase()
        engine = self._make_engine()
        result = uc.execute(engine, "Добрый день")
        self.assertEqual(result, "ответ")


class TestCheckDiagnosisUseCase(unittest.TestCase):

    def _make_patient_and_card(self, disease_type):
        patient = create_patient(disease_type)
        card = MedicalCard()
        return patient, card

    def test_correct_diagnosis_appendicitis(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.APPENDICITIS)
        result = uc.execute("Острый аппендицит", patient, card)
        self.assertIsInstance(result, DiagnosisResult)
        self.assertTrue(result.is_correct)
        self.assertGreater(result.score, 0.8)

    def test_synonym_diagnosis_appendicitis(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.APPENDICITIS)
        result = uc.execute("аппендицит", patient, card)
        self.assertTrue(result.is_correct)

    def test_correct_diagnosis_diabetes(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.DIABETES)
        result = uc.execute("Сахарный диабет 2 типа", patient, card)
        self.assertTrue(result.is_correct)

    def test_wrong_diagnosis_returns_false(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.APPENDICITIS)
        result = uc.execute("грипп", patient, card)
        self.assertFalse(result.is_correct)

    def test_wrong_diagnosis_message_contains_correct(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.APPENDICITIS)
        result = uc.execute("грипп", patient, card)
        # Сообщение должно содержать правильный диагноз
        self.assertIn("аппендицит", result.message_text.lower())

    def test_correct_diagnosis_message_has_checkmark(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.ANEMIA)
        result = uc.execute("Железодефицитная анемия", patient, card)
        self.assertIn("✅", result.message_text)

    def test_wrong_diagnosis_message_has_cross(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.ANEMIA)
        result = uc.execute("рак", patient, card)
        self.assertIn("❌", result.message_text)

    def test_result_contains_rendered_card(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.TUBERCULOSIS)
        result = uc.execute("туберкулез", patient, card)
        self.assertIn("Медицинская карта", result.rendered_card)

    def test_card_diagnosis_field_updated(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.EPILEPSY)
        uc.execute("эпилепсия", patient, card)
        self.assertEqual(card.diagnosis, "эпилепсия")

    def test_empty_diagnosis_handled(self):
        uc = CheckDiagnosisUseCase()
        patient, card = self._make_patient_and_card(DiseaseType.APPENDICITIS)
        result = uc.execute("", patient, card)
        self.assertFalse(result.is_correct)
        self.assertIsInstance(result.score, float)


class TestFacadeFunctions(unittest.TestCase):
    """Проверяем публичные функции-обёртки."""

    def setUp(self):
        self.patcher = patch("services.case_service.DialogEngine")
        self.MockEngine = self.patcher.start()
        self.MockEngine.return_value = MagicMock()

    def tearDown(self):
        self.patcher.stop()

    def test_start_random_case_returns_result(self):
        result = start_random_case()
        self.assertIsInstance(result, CaseInitResult)

    def test_start_case_by_type_appendicitis(self):
        result = start_case_by_type(DiseaseType.APPENDICITIS)
        self.assertEqual(result.patient.disease.name, "Аппендицит")

    def test_check_diagnosis_facade(self):
        patient = create_patient(DiseaseType.APPENDICITIS)
        card = MedicalCard()
        result = check_diagnosis("Острый аппендицит", patient, card)
        self.assertTrue(result.is_correct)

    def test_process_dialog_facade(self):
        patient = create_patient(DiseaseType.APPENDICITIS)
        card = MedicalCard()
        engine = DialogEngine(patient=patient, card=card, llm=FakeLLM())
        result = process_dialog(engine, "Что болит?")
        self.assertEqual(result, "ответ")


if __name__ == "__main__":
    unittest.main(verbosity=2)