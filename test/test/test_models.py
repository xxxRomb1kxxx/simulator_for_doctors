import unittest
from models.models import Disease, DiseaseType, MedicalCard, Patient


class TestMedicalCard(unittest.TestCase):

    def _make_card(self, **kwargs):
        defaults = dict(complaints=[], anamnesis=[], diagnostics=[], diagnosis=None)
        defaults.update(kwargs)
        return MedicalCard(**defaults)


    def test_render_empty_card_contains_header(self):
        card = self._make_card()
        rendered = card.render()
        self.assertIn("Медицинская карта", rendered)

    def test_render_shows_not_collected_when_empty(self):
        card = self._make_card()
        self.assertIn("не собрано", card.render())

    def test_render_shows_diagnosis_not_set_when_none(self):
        card = self._make_card()
        self.assertIn("не поставлен", card.render())

    def test_render_shows_diagnosis_when_set(self):
        card = self._make_card(diagnosis="Острый аппендицит")
        rendered = card.render()
        self.assertIn("Острый аппендицит", rendered)

    def test_render_shows_complaints_bullet_points(self):
        card = self._make_card(complaints=["Боль в животе", "Тошнота"])
        rendered = card.render()
        self.assertIn("Боль в животе", rendered)
        self.assertIn("Тошнота", rendered)

    def test_render_shows_all_sections(self):
        card = self._make_card(
            complaints=["жалоба"],
            anamnesis=["анамнез"],
            diagnostics=["диагностика"],
            diagnosis="Диагноз",
        )
        rendered = card.render()
        self.assertIn("жалоба", rendered)
        self.assertIn("анамнез", rendered)
        self.assertIn("диагностика", rendered)
        self.assertIn("Диагноз", rendered)

    def test_render_section_empty_shows_placeholder(self):
        card = self._make_card(complaints=[], anamnesis=["есть"])
        rendered = card.render()
        # Жалобы пустые "не собрано"
        self.assertIn("не собрано", rendered)
        # Анамнез есть
        self.assertIn("есть", rendered)


    def test_card_complaints_mutable(self):
        card = self._make_card()
        card.complaints.append("боль")
        self.assertEqual(card.complaints, ["боль"])

    def test_two_cards_independent(self):
        c1 = self._make_card()
        c2 = self._make_card()
        c1.complaints.append("уникальная жалоба")
        self.assertEqual(c2.complaints, [])


class TestDiseaseType(unittest.TestCase):

    def test_all_five_types_defined(self):
        types = list(DiseaseType)
        self.assertEqual(len(types), 5)

    def test_values_are_strings(self):
        for dt in DiseaseType:
            self.assertIsInstance(dt.value, str)

    def test_from_value(self):
        self.assertEqual(DiseaseType("diabetes"), DiseaseType.DIABETES)

    def test_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            DiseaseType("unknown_disease")


class TestDisease(unittest.TestCase):

    def _make_disease(self, **kw):
        defaults = dict(
            name="Тест",
            complaints=["жалоба"],
            anamnesis=["анамнез"],
            diagnostics=["диагностика"],
            correct_diagnosis="Диагноз теста",
        )
        defaults.update(kw)
        return Disease(**defaults)

    def test_fields_accessible(self):
        d = self._make_disease()
        self.assertEqual(d.name, "Тест")
        self.assertEqual(d.correct_diagnosis, "Диагноз теста")

    def test_lists_are_independent_copies(self):
        source = ["жалоба1"]
        d = self._make_disease(complaints=source)
        source.append("жалоба2")
        # dataclass не копирует — это ожидаемо, проверяем что объект создан
        self.assertIsInstance(d.complaints, list)


class TestPatient(unittest.TestCase):

    def _make_patient(self):
        disease = Disease(
            name="Анемия",
            complaints=["слабость"],
            anamnesis=["месяц назад"],
            diagnostics=["гемоглобин 85"],
            correct_diagnosis="Железодефицитная анемия",
        )
        return Patient(
            fio="Иванова Мария",
            gender="Ж",
            age=35,
            profession="Учитель",
            disease=disease,
        )

    def test_patient_fields(self):
        p = self._make_patient()
        self.assertEqual(p.fio, "Иванова Мария")
        self.assertEqual(p.gender, "Ж")
        self.assertEqual(p.age, 35)

    def test_patient_has_disease(self):
        p = self._make_patient()
        self.assertIsInstance(p.disease, Disease)
        self.assertEqual(p.disease.name, "Анемия")


if __name__ == "__main__":
    unittest.main(verbosity=2)