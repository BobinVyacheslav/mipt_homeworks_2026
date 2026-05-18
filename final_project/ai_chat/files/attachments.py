import re

from final_project.ai_chat.files.reader import read_text_file

ATTACHMENT_RE = re.compile(r'@::(.+?)::')


def expand_file_attachments(message: str) -> str:
    def replace(match: re.Match[str]) -> str:
        path = match.group(1).strip()
        content = read_text_file(path)
        return f'\n\n{content}'

    return ATTACHMENT_RE.sub(replace, message)
