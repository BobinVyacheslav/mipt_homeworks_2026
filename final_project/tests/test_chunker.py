from final_project.ai_chat.files.chunker import (
    LengthChunkStrategy,
    MultiParagraphChunkStrategy,
    ParagraphChunkStrategy,
)


def test_paragraph_strategy() -> None:
    chunks = ParagraphChunkStrategy().split('one\n\n\ntwo\n\nthree')

    assert chunks == ['one', 'two', 'three']


def test_multi_paragraph_strategy() -> None:
    chunks = MultiParagraphChunkStrategy(2).split('one\n\ntwo\n\nthree')

    assert chunks == ['one\n\ntwo', 'three']


def test_length_strategy() -> None:
    chunks = LengthChunkStrategy(3).split('abcdefg')

    assert chunks == ['abc', 'def', 'g']

