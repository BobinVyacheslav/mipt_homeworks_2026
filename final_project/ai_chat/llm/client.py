from collections.abc import Iterator
from typing import Protocol

from final_project.ai_chat.chat.message import Message


class LLMClient(Protocol):
    def send_messages(self, messages: list[Message]) -> str:
        ...

    def stream_messages(self, messages: list[Message]) -> Iterator[str]:
        ...
