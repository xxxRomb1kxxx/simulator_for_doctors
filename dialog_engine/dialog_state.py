from dataclasses import dataclass, field
from typing import List


@dataclass
class DialogState:
    """Класс для управления состоянием диалога"""
    stage: str = "greeting"
    dialog_history: List[str] = field(default_factory=list)

    def add_to_history(self, text: str):
        """Добавить реплику в историю"""
        self.dialog_history.append(text)

    def get_recent_history(self, limit: int = 10) -> str:
        """Получить последние N реплик"""
        return "\n".join(self.dialog_history[-limit:])

    def transition_stage(self, new_stage: str):
        """Переход на новую стадию диалога"""
        self.stage = new_stage