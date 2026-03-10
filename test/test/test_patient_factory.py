import unittest
from models.models import DiseaseType, Patient, Disease
from models.patient_factory import create_patient, DISEASE_DATA
from models.disease_registry import DISEASE_REGISTRY


class TestDiseaseRegistry(unittest.TestCase):

    def test_all_disease_types_registered(self):
        for dt in DiseaseType:
            self.assertIn(dt, DISEASE_REGISTRY, f"{dt} not in DISEASE_REGISTRY")

    def test_each_config_has_name(self):
        for dt, cfg in DISEASE_REGISTRY.items():
            self.assertIsInstance(cfg.name, str, f"{dt}: name must be str")
            self.assertTrue(cfg.name, f"{dt}: name must not be empty")

    def test_each_config_has_correct_diagnosis(self):
        for dt, cfg in DISEASE_REGISTRY.items():
            self.assertIsInstance(cfg.correct_diagnosis, str)
            self.assertTrue(cfg.correct_diagnosis)

    def test_each_config_has_complaints(self):
        for dt, cfg in DISEASE_REGISTRY.items():
            self.assertIsInstance(cfg.complaints, list)
            self.assertGreater(len(cfg.complaints), 0, f"{dt}: must have complaints")

    def test_each_config_has_anamnesis(self):
        for dt, cfg in DISEASE_REGISTRY.items():
            self.assertIsInstance(cfg.anamnesis, list)
            self.assertGreater(len(cfg.anamnesis), 0, f"{dt}: must have anamnesis")

    def test_each_config_has_diagnostics(self):
        for dt, cfg in DISEASE_REGISTRY.items():
            self.assertIsInstance(cfg.diagnostics, list)
            self.assertGreater(len(cfg.diagnostics), 0, f"{dt}: must have diagnostics")

    def test_each_config_has_patient_prompt(self):
        for dt, cfg in DISEASE_REGISTRY.items():
            self.assertIsInstance(cfg.patient_prompt, str)
            self.assertTrue(cfg.patient_prompt, f"{dt}: patient_prompt must not be empty")

    def test_each_config_has_synonyms(self):
        for dt, cfg in DISEASE_REGISTRY.items():
            self.assertIsInstance(cfg.synonyms, list)

    def test_registry_immutable_frozen(self):
        cfg = DISEASE_REGISTRY[DiseaseType.APPENDICITIS]
        with self.assertRaises((AttributeError, TypeError)):
            cfg.name = "Изменено"


class TestDiseaseData(unittest.TestCase):

    def test_disease_data_has_all_types(self):
        for dt in DiseaseType:
            self.assertIn(dt, DISEASE_DATA)

    def test_disease_data_structure(self):
        for dt, data in DISEASE_DATA.items():
            for key in ("name", "complaints", "anamnesis", "diagnostics", "correct_diagnosis"):
                self.assertIn(key, data, f"{dt}: missing key '{key}'")


class TestCreatePatient(unittest.TestCase):

    def test_create_patient_appendicitis(self):
        p = create_patient(DiseaseType.APPENDICITIS)
        self.assertIsInstance(p, Patient)
        self.assertEqual(p.disease.name, "Аппендицит")

    def test_create_patient_diabetes(self):
        p = create_patient(DiseaseType.DIABETES)
        self.assertEqual(p.disease.name, "Сахарный диабет")

    def test_create_patient_anemia(self):
        p = create_patient(DiseaseType.ANEMIA)
        self.assertEqual(p.disease.name, "Анемия")

    def test_create_patient_tuberculosis(self):
        p = create_patient(DiseaseType.TUBERCULOSIS)
        self.assertEqual(p.disease.name, "Туберкулёз")

    def test_create_patient_epilepsy(self):
        p = create_patient(DiseaseType.EPILEPSY)
        self.assertEqual(p.disease.name, "Эпилепсия")

    def test_patient_has_fio(self):
        p = create_patient(DiseaseType.APPENDICITIS)
        self.assertIsInstance(p.fio, str)
        self.assertTrue(p.fio)

    def test_patient_has_gender(self):
        p = create_patient(DiseaseType.APPENDICITIS)
        self.assertIn(p.gender, ("М", "Ж"))

    def test_patient_age_in_range_appendicitis(self):
        for _ in range(20):
            p = create_patient(DiseaseType.APPENDICITIS)
            self.assertGreaterEqual(p.age, 18)
            self.assertLessEqual(p.age, 40)

    def test_patient_age_in_range_diabetes(self):
        for _ in range(20):
            p = create_patient(DiseaseType.DIABETES)
            self.assertGreaterEqual(p.age, 45)
            self.assertLessEqual(p.age, 65)

    def test_patient_has_profession(self):
        p = create_patient(DiseaseType.ANEMIA)
        self.assertIsInstance(p.profession, str)
        self.assertTrue(p.profession)

    def test_patient_disease_is_disease_instance(self):
        p = create_patient(DiseaseType.TUBERCULOSIS)
        self.assertIsInstance(p.disease, Disease)

    def test_disease_fields_are_copies(self):
        p1 = create_patient(DiseaseType.APPENDICITIS)
        p2 = create_patient(DiseaseType.APPENDICITIS)
        p1.disease.complaints.append("доп жалоба")
        self.assertNotEqual(len(p1.disease.complaints), len(p2.disease.complaints))

    def test_unknown_disease_raises(self):
        with self.assertRaises((ValueError, KeyError)):
            create_patient("nonexistent_disease")  # type: ignore

    def test_randomness_produces_different_patients(self):
        patients = [create_patient(DiseaseType.APPENDICITIS) for _ in range(50)]
        fios = {p.fio for p in patients}
        ages = {p.age for p in patients}
        # После 50 попыток должны быть разные ФИО или возраст
        self.assertTrue(len(fios) > 1 or len(ages) > 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)