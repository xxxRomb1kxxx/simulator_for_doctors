from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class DialogState:
    stage: str = "greeting"
    dialog_history: List[Dict[str,Any]] = field(default_factory=list)

    def add_to_history(self, role: str, content: str):
        self.dialog_history.append({
            "role": role,
            "content": content
        })

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.dialog_history[-limit:]

    def transition_stage(self, new_stage: str):
        self.stage = new_stage
        self.add_to_history("system", f"Этап приема изменен на: {new_stage}")