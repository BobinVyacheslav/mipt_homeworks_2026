from abc import ABC, abstractmethod


class ChunkStrategy(ABC):
    @abstractmethod
    def split(self, text: str) -> list[str]:
        ...


class ParagraphChunkStrategy(ChunkStrategy):
    def split(self, text: str) -> list[str]:
        return _paragraphs(text)


class MultiParagraphChunkStrategy(ChunkStrategy):
    def __init__(self, paragraph_count: int) -> None:
        self._paragraph_count = paragraph_count

    def split(self, text: str) -> list[str]:
        paragraphs = _paragraphs(text)
        return [
            '\n\n'.join(paragraphs[index:index + self._paragraph_count])
            for index in range(0, len(paragraphs), self._paragraph_count)
        ]


class LengthChunkStrategy(ChunkStrategy):
    def __init__(self, length: int) -> None:
        self._length = length

    def split(self, text: str) -> list[str]:
        stripped = text.strip()
        if not stripped:
            return []
        return [
            stripped[index:index + self._length]
            for index in range(0, len(stripped), self._length)
        ]


def create_chunk_strategy(
    paragraph_count: int | None = None,
    length: int | None = None,
) -> ChunkStrategy:
    if length is not None:
        return LengthChunkStrategy(length)
    if paragraph_count is not None:
        return MultiParagraphChunkStrategy(paragraph_count)
    return ParagraphChunkStrategy()


def _paragraphs(text: str) -> list[str]:
    return [paragraph.strip() for paragraph in re_split_paragraphs(text) if paragraph.strip()]


def re_split_paragraphs(text: str) -> list[str]:
    return [part for part in text.replace('\r\n', '\n').split('\n\n')]
