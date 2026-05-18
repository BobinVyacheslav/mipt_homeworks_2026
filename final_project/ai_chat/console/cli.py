from final_project.ai_chat.chat.service import ChatService
from final_project.ai_chat.console.commands import Command, CommandType, parse_command
from final_project.ai_chat.console.output import (
    print_assistant,
    print_error,
    print_info,
    print_stream_token,
)
from final_project.ai_chat.console.screen import clear_screen
from final_project.ai_chat.files.attachments import expand_file_attachments
from final_project.ai_chat.files.chunker import create_chunk_strategy
from final_project.ai_chat.files.exceptions import FileProcessingError
from final_project.ai_chat.files.reader import read_text_file
from final_project.ai_chat.llm.exceptions import LLMError


class ConsoleChatApp:
    def __init__(self, chat_service: ChatService, streaming: bool = False) -> None:
        self._chat_service = chat_service
        self._streaming = streaming

    def run(self) -> None:
        while True:
            user_text = input('>>> ')
            command = parse_command(user_text)
            if command.type == CommandType.EXIT:
                print_info('Выход.')
                return
            if command.type == CommandType.RESET:
                self._chat_service.reset()
                clear_screen()
                print_info('История очищена.')
                continue
            if command.type == CommandType.FILE_CHUNK:
                self._run_file_chunk_mode(command)
                continue
            if command.type == CommandType.INVALID:
                print_error(command.error or 'Некорректная команда.')
                continue

            self._handle_message(user_text)

    def _handle_message(self, user_text: str) -> None:
        try:
            expanded_text = expand_file_attachments(user_text)
        except FileProcessingError as exc:
            print_error(str(exc))
            return

        try:
            if self._streaming:
                print('ИИ: ', end='', flush=True)
                for token in self._chat_service.ask_stream(expanded_text):
                    print_stream_token(token)
                print()
            else:
                print_assistant(self._chat_service.ask(expanded_text))
        except KeyboardInterrupt:
            print_info('\nЗапрос прерван. Можно ввести новое сообщение.')
        except LLMError as exc:
            print_error(str(exc))

    def _run_file_chunk_mode(self, command: Command) -> None:
        print_info('Введите путь до файла:')
        file_path = input('>>> ')
        if parse_command(file_path).type == CommandType.EXIT:
            return

        try:
            text = read_text_file(file_path)
        except FileProcessingError as exc:
            print_error(str(exc))
            return

        print_info('Принято. Что нужно сделать для каждого фрагмента?')
        prompt = input('>>> ')
        if parse_command(prompt).type == CommandType.EXIT:
            return

        strategy = create_chunk_strategy(command.paragraph_count, command.length)
        chunks = strategy.split(text)
        if not chunks:
            print_error('Файл пуст или не содержит текстовых фрагментов.')
            return

        print_info('Принято. Начинаю обработку:')
        for index, chunk in enumerate(chunks, start=1):
            print_info(f'\nФрагмент {index}/{len(chunks)}:')
            if not self._process_chunk(prompt, chunk):
                return
            if not command.auto_yes and index < len(chunks):
                next_action = input('Нажмите Enter для следующего фрагмента или введите \\q: ')
                if parse_command(next_action).type == CommandType.EXIT:
                    return

        print_info('Обработка файла завершена.')

    def _process_chunk(self, prompt: str, chunk: str) -> bool:
        try:
            if self._streaming:
                print('ИИ: ', end='', flush=True)
                for token in self._chat_service.ask_single_stream(prompt, chunk):
                    print_stream_token(token)
                print()
            else:
                print_assistant(self._chat_service.ask_single(prompt, chunk))
        except KeyboardInterrupt:
            print_info('\nЗапрос прерван. Можно ввести новое сообщение.')
            return False
        except LLMError as exc:
            print_error(str(exc))
            return False
        return True
