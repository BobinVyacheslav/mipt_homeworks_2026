from dataclasses import dataclass
from typing import Literal

from final_project.ai_chat.utils.text import normalize_text

Role = Literal['system', 'user', 'assistant']


@dataclass
class Message:
    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        return {'role': self.role, 'content': normalize_text(self.content)}
