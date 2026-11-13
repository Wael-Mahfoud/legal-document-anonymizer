"""Offset-preserving text chunking for model inference."""

from collections.abc import Iterator

from app.config.settings import MAX_MODEL_CHUNK_CHARS, MODEL_CHUNK_OVERLAP_CHARS


def iter_chunks_with_offsets(
    text: str,
    max_chars: int = MAX_MODEL_CHUNK_CHARS,
    overlap: int = MODEL_CHUNK_OVERLAP_CHARS,
) -> Iterator[tuple[int, str]]:
    """Yield (absolute_start, chunk) pairs while preserving enough overlap for names."""
    if not text:
        return
    start = 0
    length = len(text)
    while start < length:
        hard_end = min(start + max_chars, length)
        end = hard_end
        if hard_end < length:
            # Prefer cutting on a space/newline in the latter half of the chunk.
            lower_bound = start + max_chars // 2
            candidates = [text.rfind(" ", lower_bound, hard_end), text.rfind("\n", lower_bound, hard_end)]
            cut = max(candidates)
            if cut > start:
                end = cut
        if end <= start:
            end = min(start + max_chars, length)
        yield start, text[start:end]
        if end >= length:
            break
        next_start = max(start + 1, end - overlap)
        start = next_start
