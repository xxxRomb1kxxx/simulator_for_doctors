"""
Unit-тесты для services/diagnosis.py — check(), similarity_score().
Запуск: python -m pytest test/test_diagnosis.py -v
"""
import sys
import os

import unittest
from services.diagnosis import check, similarity_score


class TestDiagnosisCheck(unittest.TestCase):

    # --- точные совпадения ---

    def test_exact_match_appendicitis(self):
        self.assertTrue(check("Острый аппендицит", "Острый аппендицит"))

    def test_exact_match_diabetes(self):
        self.assertTrue(check("Сахарный диабет 2 типа", "Сахарный диабет 2 типа"))

    def test_exact_match_anemia(self):
        self.assertTrue(check("Железодефицитная анемия", "Железодефицитная анемия"))

    def test_exact_match_tuberculosis(self):
        self.assertTrue(check("Инфильтративный туберкулёз лёгких", "Инфильтративный туберкулез легких"))

    def test_exact_match_epilepsy(self):
        self.assertTrue(check("Идиопатическая генерализованная эпилепсия", "Идиопатическая генерализованная эпилепсия"))

    # --- синонимы и сокращённые формы ---

    def test_synonym_appendicitis_short(self):
        self.assertTrue(check("аппендицит", "Острый аппендицит"))

    def test_synonym_diabetes_short(self):
        self.assertTrue(check("диабет", "Сахарный диабет 2 типа"))

    def test_synonym_diabetes_type2(self):
        self.assertTrue(check("диабет 2 типа", "Сахарный диабет 2 типа"))

    def test_synonym_anemia_short(self):
        self.assertTrue(check("анемия", "Железодефицитная анемия"))

    def test_synonym_tuberculosis_short(self):
        self.assertTrue(check("туберкулез", "Инфильтративный туберкулез легких"))

    def test_synonym_tuberculosis_yo(self):
        # ё и е должны считаться одинаково
        self.assertTrue(check("туберкулёз", "Инфильтративный туберкулез легких"))

    def test_synonym_epilepsy_short(self):
        self.assertTrue(check("эпилепсия", "Идиопатическая генерализованная эпилепсия"))

    # --- регистр ---

    def test_case_insensitive(self):
        self.assertTrue(check("ОСТРЫЙ АППЕНДИЦИТ", "Острый аппендицит"))

    def test_case_insensitive_lower(self):
        self.assertTrue(check("острый аппендицит", "Острый аппендицит"))

    # --- неверные диагнозы ---

    def test_wrong_diagnosis_returns_false(self):
        self.assertFalse(check("грипп", "Острый аппендицит"))

    def test_completely_wrong_returns_false(self):
        self.assertFalse(check("здоров", "Сахарный диабет 2 типа"))

    def test_empty_string_returns_false(self):
        self.assertFalse(check("", "Острый аппендицит"))

    def test_nonsense_returns_false(self):
        self.assertFalse(check("asdjfklasdjf", "Железодефицитная анемия"))

    # --- пограничные случаи ---

    def test_correct_with_extra_spaces(self):
        self.assertTrue(check("  острый аппендицит  ", "Острый аппендицит"))

    def test_diabetes_long_form(self):
        self.assertTrue(check("Сахарный диабет 2 типа", "Сахарный диабет 2 типа"))


class TestSimilarityScore(unittest.TestCase):

    def test_exact_match_score_is_1(self):
        score = similarity_score("Острый аппендицит", "Острый аппендицит")
        self.assertAlmostEqual(score, 1.0, places=2)

    def test_synonym_score_is_1(self):
        score = similarity_score("аппендицит", "Острый аппендицит")
        self.assertAlmostEqual(score, 1.0, places=2)

    def test_wrong_diagnosis_low_score(self):
        score = similarity_score("грипп", "Острый аппендицит")
        self.assertLess(score, 0.5)

    def test_score_between_0_and_1(self):
        score = similarity_score("что-то непонятное", "Железодефицитная анемия")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_partial_match_medium_score(self):
        # "анемия" — синоним железодефицитной анемии → должен быть высокий score
        score = similarity_score("анемия", "Железодефицитная анемия")
        self.assertGreater(score, 0.8)

    def test_empty_user_low_score(self):
        score = similarity_score("", "Острый аппендицит")
        self.assertLess(score, 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)