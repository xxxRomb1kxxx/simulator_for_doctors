import pytest
from models.entities.medical_card import MedicalCard


class TestMedicalCard:

    def test_medical_card_creation(self):
        card = MedicalCard()
        assert hasattr(card, 'complaints')
        assert hasattr(card, 'anamnesis')
        assert hasattr(card, 'diagnosis')
        assert card.diagnosis is None
        assert isinstance(card.complaints, list)
        assert isinstance(card.anamnesis, list)

    def test_add_complaint(self):
        card = MedicalCard()
        card.complaints.append("Болит голова")
        assert "Болит голова" in card.complaints
        assert len(card.complaints) == 1

    def test_add_anamnesis(self):
        card = MedicalCard()
        card.anamnesis.append("Болеет 3 дня")
        assert "Болеет 3 дня" in card.anamnesis
        assert len(card.anamnesis) == 1

    def test_set_diagnosis(self):
        card = MedicalCard()
        card.diagnosis = "Острый аппендицит"
        assert card.diagnosis == "Острый аппендицит"

    def test_render(self):
        card = MedicalCard()
        card.complaints.append("Боль в животе")
        card.anamnesis.append("Началось 6 часов назад")
        card.diagnosis = "Аппендицит"

        rendered = card.render()
        assert isinstance(rendered, str)
        assert "Боль в животе" in rendered
        assert "Аппендицит" in rendered