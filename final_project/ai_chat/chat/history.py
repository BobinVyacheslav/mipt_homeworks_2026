from final_project.ai_chat.chat.message import Message
from final_project.ai_chat.utils.text import normalize_text


class ChatHistory:
    def __init__(self, system_prompt: str | None = None) -> None:
        self._system_prompt = system_prompt
        self._messages: list[Message] = []
        self.reset()

    @property
    def system_prompt(self) -> str | None:
        return self._system_prompt

    @property
    def messages(self) -> list[Message]:
        return self._messages

    def add_user_message(self, content: str) -> None:
        self._messages.append(Message(role='user', content=normalize_text(content)))

    def add_assistant_message(self, content: str) -> None:
        self._messages.append(Message(role='assistant', content=normalize_text(content)))

    def reset(self) -> None:
        self._messages = []
        if self._system_prompt:
            self._messages.append(
                Message(role='system', content=normalize_text(self._system_prompt))
            )

    def total_chars(self) -> int:
        return sum(len(message.content) for message in self._messages)
