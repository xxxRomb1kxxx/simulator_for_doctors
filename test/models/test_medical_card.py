import pytest

from models.entities.medical_card import MedicalCard


class TestMedicalCard:

    def test_default_state(self) -> None:
        card = MedicalCard()
        assert card.complaints == []
        assert card.anamnesis == []
        assert card.diagnostics == []
        assert card.diagnosis is None

    def test_render_empty_card(self) -> None:
        """ИСПРАВЛЕН баг оригинала: render() крашился на пустых списках."""
        card = MedicalCard()
        rendered = card.render()
        assert isinstance(rendered, str)
        assert "не собрано" in rendered
        assert "не поставлен" in rendered

    def test_render_filled_card(self) -> None:
        card = MedicalCard(
            complaints=["Боль в животе"],
            anamnesis=["Болит 6 часов"],
            diagnostics=["УЗИ"],
            diagnosis="Острый аппендицит",
        )
        rendered = card.render()
        assert "Боль в животе" in rendered
        assert "Болит 6 часов" in rendered
        assert "УЗИ" in rendered
        assert "Острый аппендицит" in rendered

    def test_render_partial_card(self) -> None:
        card = MedicalCard(complaints=["Кашель"])
        rendered = card.render()
        assert "Кашель" in rendered
        assert "не собрано" in rendered  # anamnesis и diagnostics пустые
