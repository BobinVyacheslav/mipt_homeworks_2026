from dataclasses import dataclass
from enum import Enum


class CommandType(str, Enum):
    MESSAGE = 'message'
    EXIT = 'exit'
    RESET = 'reset'
    FILE_CHUNK = 'file_chunk'
    INVALID = 'invalid'


@dataclass(frozen=True)
class Command:
    type: CommandType
    raw_text: str
    paragraph_count: int | None = None
    length: int | None = None
    auto_yes: bool = False
    error: str | None = None


def parse_command(raw_text: str) -> Command:
    text = raw_text.strip()
    if text == r'\q':
        return Command(type=CommandType.EXIT, raw_text=raw_text)
    if text == '/reset':
        return Command(type=CommandType.RESET, raw_text=raw_text)
    if text.startswith('/filechunk') or text.startswith('/file_chunk'):
        return _parse_file_chunk(raw_text, text)
    return Command(type=CommandType.MESSAGE, raw_text=raw_text)


def _parse_file_chunk(raw_text: str, text: str) -> Command:
    parts = text.split()
    command_name = parts[0]
    if command_name not in {'/filechunk', '/file_chunk'}:
        return Command(
            type=CommandType.INVALID,
            raw_text=raw_text,
            error='Неизвестная команда. Возможно, вы имели в виду /filechunk.',
        )

    paragraph_count: int | None = None
    length: int | None = None
    auto_yes = False

    for part in parts[1:]:
        if part == '-y':
            auto_yes = True
            continue
        if part.startswith('paragraph='):
            parsed = _parse_positive_arg(part, 'paragraph')
            if parsed is None:
                return _invalid(raw_text, 'paragraph должен быть положительным целым числом.')
            paragraph_count = parsed
            continue
        if part.startswith('len='):
            parsed = _parse_positive_arg(part, 'len')
            if parsed is None:
                return _invalid(raw_text, 'len должен быть положительным целым числом.')
            length = parsed
            continue
        return _invalid(raw_text, f'Некорректный параметр команды /filechunk: {part}')

    if paragraph_count is not None and length is not None:
        return _invalid(raw_text, 'Нельзя одновременно указывать paragraph и len.')

    return Command(
        type=CommandType.FILE_CHUNK,
        raw_text=raw_text,
        paragraph_count=paragraph_count,
        length=length,
        auto_yes=auto_yes,
    )


def _parse_positive_arg(part: str, name: str) -> int | None:
    raw_value = part.removeprefix(f'{name}=')
    try:
        value = int(raw_value)
    except ValueError:
        return None
    if value <= 0:
        return None
    return value


def _invalid(raw_text: str, error: str) -> Command:
    return Command(type=CommandType.INVALID, raw_text=raw_text, error=error)
