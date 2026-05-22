from collections.abc import Callable
from importlib import import_module
from typing import Any, Protocol, cast

from final_project.ai_chat.utils.text import normalize_text


class ConsoleLike(Protocol):
    file: Any

    def print(self, *objects: object, **kwargs: Any) -> None: ...

    def input(self, prompt: str = '', **kwargs: Any) -> str: ...


def _load_rich() -> tuple[ConsoleLike, Callable[..., object], Callable[..., object]]:
    console_module = import_module('rich.console')
    markdown_module = import_module('rich.markdown')
    panel_module = import_module('rich.panel')
    console_class = vars(console_module)['Console']
    markdown_class = vars(markdown_module)['Markdown']
    panel_class = vars(panel_module)['Panel']
    return (
        cast(ConsoleLike, console_class()),
        cast(Callable[..., object], markdown_class),
        cast(Callable[..., object], panel_class),
    )


console, Markdown, Panel = _load_rich()


def print_welcome() -> None:
    console.print(
        Panel(
            'Введите сообщение или команду: [bold]/reset[/bold], '
            '[bold]/filechunk[/bold], [bold]\\q[/bold]',
            title='AI Chat',
            border_style='cyan',
        )
    )


def print_error(message: str) -> None:
    console.print(f'[bold red]Ошибка:[/bold red] {normalize_text(message)}')


def print_info(message: str) -> None:
    console.print(f'[cyan]{normalize_text(message)}[/cyan]')


def print_success(message: str) -> None:
    console.print(f'[green]{normalize_text(message)}[/green]')


def print_assistant(message: str) -> None:
    console.print(
        Panel(
            Markdown(normalize_text(message)),
            title='ИИ',
            border_style='green',
        )
    )


def print_stream_start() -> None:
    console.print('[bold green]ИИ:[/bold green] ', end='')


def print_stream_token(token: str) -> None:
    console.print(normalize_text(token), end='', markup=False, highlight=False, soft_wrap=True)
    console.file.flush()


def print_stream_end() -> None:
    console.print()


def read_user_input(prompt: str = '>>> ') -> str:
    return console.input(f'[bold cyan]{prompt}[/bold cyan]')
