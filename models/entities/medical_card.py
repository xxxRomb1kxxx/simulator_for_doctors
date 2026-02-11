from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class MedicalCard:
    complaints: List[str] = field(default_factory=list)
    anamnesis: List[str] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    diagnosis: Optional[str] = None

    def render(self) -> str:
        return (
            "📋 Медицинская карта\n\n"
            f"Жалобы:\n- " + "\n- ".join(self.complaints) + "\n\n"
            f"Анамнез:\n- " + "\n- ".join(self.anamnesis) + "\n\n"
            f"Диагностика:\n- " + "\n- ".join(self.diagnostics) + "\n\n"
            f"Диагноз: {self.diagnosis}"
        )
