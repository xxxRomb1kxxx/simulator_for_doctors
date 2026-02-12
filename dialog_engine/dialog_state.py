from dataclasses import dataclass, field
from typing import List


@dataclass
class DialogState:
    stage: str = "greeting"
    dialog_history: List[str] = field(default_factory=list)

    def add_to_history(self, text: str):
        self.dialog_history.append(text)

    def get_recent_history(self, limit: int = 10) -> str:
        return "\n".join(self.dialog_history[-limit:])

    def transition_stage(self, new_stage: str):
        self.stage = new_stage