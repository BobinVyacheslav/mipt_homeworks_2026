from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    api_key: str
    api_host: str
    model: str = 'gpt-4o-mini'
    limit_messages: int | None = None
    limit_chars: int | None = None
    temperature: float = 0.7
    streaming: bool = False
    system_prompt: str | None = None
