import pytest

from final_project.ai_chat.console.commands import CommandType, parse_command


def test_parse_regular_message() -> None:
    command = parse_command('hello')

    assert command.type == CommandType.MESSAGE


def test_parse_exit_and_reset() -> None:
    assert parse_command(r'\q').type == CommandType.EXIT
    assert parse_command('/reset').type == CommandType.RESET


@pytest.mark.parametrize('name', ['/filechunk', '/file_chunk'])
def test_parse_file_chunk_default(name: str) -> None:
    command = parse_command(name)

    assert command.type == CommandType.FILE_CHUNK
    assert command.paragraph_count is None
    assert command.length is None


def test_parse_file_chunk_paragraph_auto_yes() -> None:
    command = parse_command('/filechunk paragraph=3 -y')

    assert command.type == CommandType.FILE_CHUNK
    assert command.paragraph_count == 3
    assert command.length is None
    assert command.auto_yes is True


def test_parse_file_chunk_length() -> None:
    command = parse_command('/file_chunk len=150')

    assert command.type == CommandType.FILE_CHUNK
    assert command.length == 150


def test_parse_file_chunk_conflicting_args() -> None:
    command = parse_command('/filechunk paragraph=3 len=150')

    assert command.type == CommandType.INVALID
    assert command.error is not None

