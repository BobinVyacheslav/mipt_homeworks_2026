from pathlib import Path
from typing import Any
from importlib import import_module
import os

from final_project.ai_chat.config.models import AppConfig
from final_project.ai_chat.config.validators import (
    ConfigError,
    parse_bool,
    parse_positive_int,
    parse_temperature,
    require_string,
)

CONFIG_FILENAME = 'config.yaml'

ENV_MAPPING = {
    'API_KEY': 'api_key',
    'API_HOST': 'api_host',
    'MODEL': 'model',
    'LIMIT_MESSAGES': 'limit_messages',
    'LIMIT_CHARS': 'limit_chars',
    'TEMPERATURE': 'temperature',
    'STREAMING': 'streaming',
    'SYSTEM_PROMPT': 'system_prompt',
}


def load_config(config_path: Path | None = None) -> AppConfig:
    _load_dotenv_if_available()
    path = config_path or Path.cwd() / CONFIG_FILENAME
    yaml_data = _load_yaml(path)
    env_data = _load_env()

    if not yaml_data and not env_data:
        raise ConfigError(
            'Не найден config.yaml и не заданы переменные окружения для конфигурации.'
        )

    merged = {**yaml_data, **env_data}
    return _build_config(merged)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    if not path.is_file():
        raise ConfigError(f'{path} должен быть файлом конфигурации.')

    try:
        content = path.read_text(encoding='utf-8')
    except OSError as exc:
        raise ConfigError(f'Не удалось открыть config.yaml: {exc}') from exc

    loaded = _parse_yaml(content)

    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ConfigError('config.yaml должен содержать словарь настроек.')
    return loaded


def _load_env() -> dict[str, str]:
    result: dict[str, str] = {}
    for env_name, config_name in ENV_MAPPING.items():
        value = os.getenv(env_name)
        if value is not None:
            result[config_name] = value
    return result


def _build_config(data: dict[str, Any]) -> AppConfig:
    return AppConfig(
        api_key=require_string(data.get('api_key'), 'api_key'),
        api_host=require_string(data.get('api_host'), 'api_host'),
        model=str(data.get('model') or 'gpt-4o-mini'),
        limit_messages=parse_positive_int(data.get('limit_messages'), 'limit_messages'),
        limit_chars=parse_positive_int(data.get('limit_chars'), 'limit_chars'),
        temperature=parse_temperature(data.get('temperature')),
        streaming=parse_bool(data.get('streaming'), 'streaming'),
        system_prompt=_optional_string(data.get('system_prompt')),
    )


def _optional_string(value: Any) -> str | None:
    if value is None or str(value).strip() == '':
        return None
    return str(value)


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _parse_yaml(content: str) -> Any:
    try:
        yaml_module = import_module('yaml')
    except ImportError:
        return _parse_simple_yaml(content)

    try:
        return yaml_module.safe_load(content)
    except Exception as exc:
        raise ConfigError(f'Не удалось прочитать YAML-конфиг: {exc}') from exc


def _parse_simple_yaml(content: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if ':' not in stripped:
            raise ConfigError('config.yaml содержит строку без разделителя ":".')
        key, value = stripped.split(':', 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result
