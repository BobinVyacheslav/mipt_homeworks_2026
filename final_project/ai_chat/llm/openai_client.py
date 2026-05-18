from collections.abc import Iterator
from importlib import import_module
from typing import Any

from final_project.ai_chat.chat.message import Message
from final_project.ai_chat.llm.exceptions import EmptyLLMResponseError, LLMError
from final_project.ai_chat.utils.text import normalize_text


class OpenAICompatibleClient:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float,
    ) -> None:
        openai_module = import_module('openai')
        self._client = openai_module.OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._temperature = temperature

    def send_messages(self, messages: list[Message]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[message.to_dict() for message in messages],
                temperature=self._temperature,
            )
        except Exception as exc:
            raise LLMError(f'Ошибка LLM API: {exc}') from exc

        content = response.choices[0].message.content
        if not content:
            raise EmptyLLMResponseError('Модель вернула пустой ответ.')
        return normalize_text(content)

    def stream_messages(self, messages: list[Message]) -> Iterator[str]:
        try:
            stream = self._client.chat.completions.create(
                model=self._model,
                messages=[message.to_dict() for message in messages],
                temperature=self._temperature,
                stream=True,
            )
            for event in stream:
                content = _extract_stream_content(event)
                if content:
                    yield normalize_text(content)
        except Exception as exc:
            raise LLMError(f'Ошибка LLM API: {exc}') from exc


def _extract_stream_content(event: Any) -> str | None:
    choices = getattr(event, 'choices', None)
    if not choices:
        return None
    delta = getattr(choices[0], 'delta', None)
    return getattr(delta, 'content', None)
