from pathlib import Path

import pytest

from final_project.ai_chat.config.loader import ENV_MAPPING, load_config
from final_project.ai_chat.config.validators import ConfigError


def clear_config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for env_name in ENV_MAPPING:
        monkeypatch.delenv(env_name, raising=False)


def test_load_config_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(
        '\n'.join(
            [
                'api_key: yaml-key',
                'api_host: http://localhost:11434/v1/',
                'model: llama3.1',
                'limit_messages: 5',
                'limit_chars: 100',
                'temperature: 0.5',
                'streaming: true',
                'system_prompt: Be useful',
            ]
        ),
        encoding='utf-8',
    )

    config = load_config(config_path)

    assert config.api_key == 'yaml-key'
    assert config.api_host == 'http://localhost:11434/v1/'
    assert config.model == 'llama3.1'
    assert config.limit_messages == 5
    assert config.limit_chars == 100
    assert config.temperature == 0.5
    assert config.streaming is True
    assert config.system_prompt == 'Be useful'


def test_env_overrides_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(
        'api_key: yaml-key\napi_host: http://yaml.example/v1/\nmodel: yaml-model\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('API_KEY', 'env-key')
    monkeypatch.setenv('MODEL', 'env-model')

    config = load_config(config_path)

    assert config.api_key == 'env-key'
    assert config.api_host == 'http://yaml.example/v1/'
    assert config.model == 'env-model'


def test_missing_config_and_env_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)

    with pytest.raises(ConfigError, match='Не найден config.yaml'):
        load_config(tmp_path / 'missing.yaml')


@pytest.mark.parametrize(
    ('field', 'value', 'message'),
    [
        ('TEMPERATURE', '2', 'temperature'),
        ('LIMIT_MESSAGES', '-1', 'limit_messages'),
        ('LIMIT_CHARS', '0', 'limit_chars'),
        ('STREAMING', 'perhaps', 'streaming'),
    ],
)
def test_invalid_env_values_raise(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: str,
    message: str,
) -> None:
    clear_config_env(monkeypatch)
    monkeypatch.setenv('API_KEY', 'key')
    monkeypatch.setenv('API_HOST', 'http://localhost:11434/v1/')
    monkeypatch.setenv(field, value)

    with pytest.raises(ConfigError, match=message):
        load_config(tmp_path / 'missing.yaml')

