from final_project.ai_chat.chat.history import ChatHistory
from final_project.ai_chat.chat.message import Message


class ContextLimiter:
    def __init__(self, limit_messages: int | None = None, limit_chars: int | None = None) -> None:
        self._limit_messages = limit_messages
        self._limit_chars = limit_chars

    def apply(self, history: ChatHistory) -> None:
        self._apply_message_limit(history)
        self._apply_char_limit(history)

    def _apply_message_limit(self, history: ChatHistory) -> None:
        if self._limit_messages is None:
            return

        messages = history.messages
        while len(messages) > self._limit_messages:
            index = self._oldest_removable_index(messages)
            if index is None:
                break
            del messages[index]

    def _apply_char_limit(self, history: ChatHistory) -> None:
        if self._limit_chars is None:
            return

        messages = history.messages
        while history.total_chars() > self._limit_chars:
            index = self._oldest_removable_index(messages)
            if index is None:
                break

            if self._has_another_removable(messages, index):
                del messages[index]
                continue

            self._trim_message_to_fit(history, index)
            break

    @staticmethod
    def _oldest_removable_index(messages: list[Message]) -> int | None:
        for index, message in enumerate(messages):
            if getattr(message, 'role', None) != 'system':
                return index
        return None

    @staticmethod
    def _has_another_removable(messages: list[Message], current_index: int) -> bool:
        for index, message in enumerate(messages):
            if index != current_index and getattr(message, 'role', None) != 'system':
                return True
        return False

    def _trim_message_to_fit(self, history: ChatHistory, index: int) -> None:
        messages = history.messages
        message = messages[index]
        other_chars = history.total_chars() - len(message.content)
        allowed_chars = max((self._limit_chars or 0) - other_chars, 0)
        message.content = message.content[-allowed_chars:] if allowed_chars else ''
