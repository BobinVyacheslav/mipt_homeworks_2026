from collections.abc import Iterator

from final_project.ai_chat.chat.context_limiter import ContextLimiter
from final_project.ai_chat.chat.history import ChatHistory
from final_project.ai_chat.chat.message import Message
from final_project.ai_chat.llm.client import LLMClient
from final_project.ai_chat.llm.exceptions import EmptyLLMResponseError


class ChatService:
    def __init__(
        self,
        client: LLMClient,
        history: ChatHistory,
        limiter: ContextLimiter,
    ) -> None:
        self._client = client
        self._history = history
        self._limiter = limiter

    @property
    def history(self) -> ChatHistory:
        return self._history

    def ask(self, user_text: str) -> str:
        self._history.add_user_message(user_text)
        self._limiter.apply(self._history)
        answer = self._client.send_messages(self._history.messages)
        if not answer:
            raise EmptyLLMResponseError('Модель вернула пустой ответ.')
        self._history.add_assistant_message(answer)
        self._limiter.apply(self._history)
        return answer

    def ask_stream(self, user_text: str) -> Iterator[str]:
        self._history.add_user_message(user_text)
        self._limiter.apply(self._history)

        chunks: list[str] = []
        for chunk in self._client.stream_messages(self._history.messages):
            chunks.append(chunk)
            yield chunk

        answer = ''.join(chunks)
        if not answer:
            raise EmptyLLMResponseError('Модель вернула пустой ответ.')
        self._history.add_assistant_message(answer)
        self._limiter.apply(self._history)

    def reset(self) -> None:
        self._history.reset()

    def ask_single(self, prompt: str, text: str) -> str:
        messages = self._single_request_messages(prompt, text)
        answer = self._client.send_messages(messages)
        if not answer:
            raise EmptyLLMResponseError('Модель вернула пустой ответ.')
        return answer

    def ask_single_stream(self, prompt: str, text: str) -> Iterator[str]:
        messages = self._single_request_messages(prompt, text)
        chunks: list[str] = []
        for chunk in self._client.stream_messages(messages):
            chunks.append(chunk)
            yield chunk

        if not ''.join(chunks):
            raise EmptyLLMResponseError('Модель вернула пустой ответ.')

    def _single_request_messages(self, prompt: str, text: str) -> list[Message]:
        messages: list[Message] = []
        if self._history.system_prompt:
            messages.append(Message(role='system', content=self._history.system_prompt))
        messages.append(Message(role='user', content=f'{prompt}\n\n{text}'))
        return messages
