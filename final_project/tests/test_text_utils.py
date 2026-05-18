from final_project.ai_chat.chat.message import Message
from final_project.ai_chat.utils.text import normalize_text


def test_normalize_text_repairs_surrogateescape_utf8() -> None:
    assert normalize_text('\udcd0\udc9f\udcd1\udc80\udcd0\udcb8') == 'При'


def test_normalize_text_replaces_broken_surrogate() -> None:
    normalized = normalize_text('bad \udcd0 text')

    normalized.encode('utf-8')
    assert '\udcd0' not in normalized


def test_message_to_dict_returns_utf8_safe_content() -> None:
    result = Message(role='user', content='bad \udcd0 text').to_dict()

    result['content'].encode('utf-8')
    assert '\udcd0' not in result['content']
