from pathlib import Path

import pytest

from final_project.ai_chat.files.attachments import expand_file_attachments
from final_project.ai_chat.files.exceptions import FileAttachmentError
from final_project.ai_chat.files.reader import MAX_FILE_SIZE_BYTES, read_text_file


def test_expand_multiple_file_attachments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    first = tmp_path / 'first.txt'
    second = tmp_path / 'second.txt'
    first.write_text('one', encoding='utf-8')
    second.write_text('two', encoding='utf-8')

    result = expand_file_attachments('Files: @::first.txt:: and @::second.txt::')

    assert 'one' in result
    assert 'two' in result
    assert '@::' not in result


def test_missing_file_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileAttachmentError, match='Файл не найден'):
        expand_file_attachments('Read @::missing.txt::')


def test_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(FileAttachmentError, match='Путь не является файлом'):
        read_text_file(tmp_path)


def test_large_file_raises(tmp_path: Path) -> None:
    path = tmp_path / 'large.txt'
    path.write_bytes(b'x' * (MAX_FILE_SIZE_BYTES + 1))

    with pytest.raises(FileAttachmentError, match='Файл больше 5 МБ'):
        read_text_file(path)
