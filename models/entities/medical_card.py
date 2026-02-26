from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MedicalCard:
    complaints: List[str] = field(default_factory=list)
    anamnesis: List[str] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    diagnosis: Optional[str] = None

    def _render_section(self, title: str, items: List[str]) -> str:
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
