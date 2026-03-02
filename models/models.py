from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional


class DiseaseType(str, Enum):
    DIABETES = "diabetes"
    ANEMIA = "anemia"
    TUBERCULOSIS = "tuberculosis"
    APPENDICITIS = "appendicitis"
    EPILEPSY = "epilepsy"


Gender = Literal["М", "Ж"]


@dataclass
class Disease:
    name: str
    complaints: list[str]
    anamnesis: list[str]
    diagnostics: list[str]
    correct_diagnosis: str


@dataclass
class Patient:
    fio: str
    gender: Gender
    age: int
    profession: str
    disease: Disease


@dataclass
class MedicalCard:
    complaints: list[str] = field(default_factory=list)
    anamnesis: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)
    diagnosis: Optional[str] = None

    def _render_section(self, title: str, items: list[str]) -> str:
        if not items:
            return f"{title}\n  — не собрано\n"
        return title + "\n" + "\n".join(f"  • {item}" for item in items) + "\n"

    def render(self) -> str:
        parts = [
            "📋 <b>Медицинская карта пациента</b>\n",
            self._render_section("📌 <b>Жалобы:</b>", self.complaints),
            self._render_section("📖 <b>Анамнез:</b>", self.anamnesis),
            self._render_section("🔬 <b>Диагностика:</b>", self.diagnostics),
            f"🩺 <b>Диагноз:</b> {self.diagnosis or 'не поставлен'}",
        ]
        return "\n".join(parts)
