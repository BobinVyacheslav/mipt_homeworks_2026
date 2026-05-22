from final_project.ai_chat.chat.history import ChatHistory


def test_reset_keeps_system_prompt() -> None:
    history = ChatHistory(system_prompt='Stay')
    history.add_user_message('hello')
    history.add_assistant_message('world')

    history.reset()

    assert len(history.messages) == 1
    assert history.messages[0].role == 'system'
    assert history.messages[0].content == 'Stay'


def test_total_chars_counts_all_messages() -> None:
    history = ChatHistory()
    history.add_user_message('abc')
    history.add_assistant_message('defg')

    assert history.total_chars() == 7
