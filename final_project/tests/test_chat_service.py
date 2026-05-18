from collections.abc import Iterator

import pytest

from final_project.ai_chat.chat.context_limiter import ContextLimiter
from final_project.ai_chat.chat.history import ChatHistory
from final_project.ai_chat.chat.message import Message
from final_project.ai_chat.chat.service import ChatService
from final_project.ai_chat.llm.exceptions import EmptyLLMResponseError


class FakeClient:
    def __init__(self, answer: str = 'answer', chunks: list[str] | None = None) -> None:
        self.answer = answer
        self.chunks = chunks or ['str', 'eam']
        self.requests: list[list[Message]] = []

    def send_messages(self, messages: list[Message]) -> str:
        self.requests.append(list(messages))
        return self.answer

    def stream_messages(self, messages: list[Message]) -> Iterator[str]:
        self.requests.append(list(messages))
        yield from self.chunks


def test_ask_updates_history_and_sends_context() -> None:
    client = FakeClient(answer='hello')
    history = ChatHistory(system_prompt='sys')
    service = ChatService(client, history, ContextLimiter())

    answer = service.ask('hi')

    assert answer == 'hello'
    assert [message.role for message in history.messages] == ['system', 'user', 'assistant']
    assert client.requests[0][0].content == 'sys'
    assert client.requests[0][1].content == 'hi'


def test_ask_stream_saves_full_answer() -> None:
    client = FakeClient(chunks=['a', 'b', 'c'])
    history = ChatHistory()
    service = ChatService(client, history, ContextLimiter())

    chunks = list(service.ask_stream('hi'))

    assert chunks == ['a', 'b', 'c']
    assert history.messages[-1].role == 'assistant'
    assert history.messages[-1].content == 'abc'


def test_ask_single_does_not_touch_main_history() -> None:
    client = FakeClient(answer='chunk answer')
    history = ChatHistory(system_prompt='sys')
    service = ChatService(client, history, ContextLimiter())

    answer = service.ask_single('summarize', 'text')

    assert answer == 'chunk answer'
    assert len(history.messages) == 1
    assert client.requests[0][0].role == 'system'
    assert client.requests[0][1].content == 'summarize\n\ntext'


def test_empty_answer_raises() -> None:
    service = ChatService(FakeClient(answer=''), ChatHistory(), ContextLimiter())

    with pytest.raises(EmptyLLMResponseError):
        service.ask('hi')

