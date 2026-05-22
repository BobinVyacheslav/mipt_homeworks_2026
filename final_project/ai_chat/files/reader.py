from pathlib import Path
import locale

from final_project.ai_chat.files.exceptions import FileAttachmentError

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


def read_text_file(path: str | Path) -> str:
    file_path = Path(path).expanduser()
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path

    if not file_path.exists():
        raise FileAttachmentError(f'Файл не найден: {file_path}')
    if not file_path.is_file():
        raise FileAttachmentError(f'Путь не является файлом: {file_path}')

    try:
        size = file_path.stat().st_size
    except OSError as exc:
        raise FileAttachmentError(f'Не удалось получить размер файла: {file_path}') from exc

    if size > MAX_FILE_SIZE_BYTES:
        raise FileAttachmentError(f'Файл больше 5 МБ: {file_path}')

    for encoding in _candidate_encodings():
        try:
            content = file_path.read_text(encoding=encoding)
            if '\x00' in content:
                raise FileAttachmentError(f'Файл не похож на текстовый файл: {file_path}')
            return content
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            raise FileAttachmentError(f'Не удалось прочитать файл: {file_path}') from exc

    raise FileAttachmentError(f'Файл не похож на текстовый UTF-8 файл: {file_path}')


def _candidate_encodings() -> list[str]:
    preferred = locale.getpreferredencoding(False)
    encodings = ['utf-8']
    if preferred and preferred.lower() != 'utf-8':
        encodings.append(preferred)
    return encodings
