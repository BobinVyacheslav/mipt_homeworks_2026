def print_error(message: str) -> None:
    print(f'Ошибка: {message}')


def print_info(message: str) -> None:
    print(message)


def print_assistant(message: str) -> None:
    print(f'ИИ: {message}')


def print_stream_token(token: str) -> None:
    print(token, end='', flush=True)
