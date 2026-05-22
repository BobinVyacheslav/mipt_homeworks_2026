def normalize_text(text: str) -> str:
    try:
        text.encode('utf-8')
    except UnicodeEncodeError:
        return _repair_surrogate_text(text)
    return text


def _repair_surrogate_text(text: str) -> str:
    try:
        return text.encode('utf-8', errors='surrogateescape').decode(
            'utf-8',
            errors='replace',
        )
    except UnicodeEncodeError:
        return text.encode('utf-8', errors='replace').decode('utf-8')
