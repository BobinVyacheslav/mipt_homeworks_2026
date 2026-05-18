from typing import Any


class ConfigError(Exception):
    pass


def parse_positive_int(value: Any, field_name: str) -> int | None:
    if value is None or value == '':
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f'Поле {field_name} должно быть положительным целым числом.') from exc
    if parsed <= 0:
        raise ConfigError(f'Поле {field_name} должно быть положительным целым числом.')
    return parsed


def parse_temperature(value: Any) -> float:
    if value is None or value == '':
        return 0.7
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError('Поле temperature должно быть числом от 0 до 1.') from exc
    if parsed < 0 or parsed > 1:
        raise ConfigError('Поле temperature должно быть числом от 0 до 1.')
    return parsed


def parse_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == '':
        return False

    normalized = str(value).strip().lower()
    if normalized in {'true', '1', 'yes', 'y', 'да'}:
        return True
    if normalized in {'false', '0', 'no', 'n', 'нет'}:
        return False
    raise ConfigError(f'Поле {field_name} должно быть true/false, 1/0 или yes/no.')


def require_string(value: Any, field_name: str) -> str:
    if value is None or str(value).strip() == '':
        raise ConfigError(f'Обязательное поле {field_name} не задано.')
    return str(value)
