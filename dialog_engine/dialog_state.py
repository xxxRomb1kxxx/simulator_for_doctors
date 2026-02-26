from dataclasses import dataclass, field
from typing import Any


@dataclass
class DialogState:
    stage: str = "greeting"
    dialog_history: list[dict[str, Any]] = field(default_factory=list)

    def add_to_history(self, role: str, content: str) -> None:
        self.dialog_history.append({"role": role, "content": content})

    def get_recent_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.dialog_history[-limit:]

    def transition_stage(self, new_stage: str) -> None:
        self.stage = new_stage
