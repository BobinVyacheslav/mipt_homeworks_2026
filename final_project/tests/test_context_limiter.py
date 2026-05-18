from final_project.ai_chat.chat.context_limiter import ContextLimiter
from final_project.ai_chat.chat.history import ChatHistory


def test_limit_messages_preserves_system_prompt() -> None:
    history = ChatHistory(system_prompt='System')
    history.add_user_message('one')
    history.add_assistant_message('two')
    history.add_user_message('three')

    ContextLimiter(limit_messages=3).apply(history)

    assert [message.role for message in history.messages] == ['system', 'assistant', 'user']
    assert history.messages[0].content == 'System'


def test_limit_chars_removes_oldest_messages() -> None:
    history = ChatHistory(system_prompt='sys')
    history.add_user_message('a' * 10)
    history.add_assistant_message('b' * 10)
    history.add_user_message('c' * 5)

    ContextLimiter(limit_chars=18).apply(history)

    assert history.messages[0].role == 'system'
    assert history.total_chars() <= 18
    assert history.messages[-1].content == 'c' * 5


def test_long_single_message_is_trimmed_from_left() -> None:
    history = ChatHistory()
    history.add_user_message('0123456789')

    ContextLimiter(limit_chars=4).apply(history)

    assert history.messages[0].content == '6789'

