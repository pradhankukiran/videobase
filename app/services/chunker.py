from app.config import (
    CHUNK_GAP_THRESHOLD,
    CHUNK_MAX_SEGMENTS,
    CHUNK_MAX_WORDS,
    CHUNK_MIN_SEGMENTS,
    CHUNK_OVERLAP,
)
from app.models.schemas import Chunk, Segment


def chunk_segments(segments: list[Segment]) -> list[Chunk]:
    """Group consecutive subtitle segments into searchable chunks.

    Uses a sliding window with overlap to prevent boundary blindness.
    Forces a chunk boundary on large time gaps (scene changes).
    """
    if not segments:
        return []

    chunks: list[Chunk] = []
    i = 0
    chunk_index = 0

    while i < len(segments):
        group: list[Segment] = [segments[i]]
        j = i + 1

        while j < len(segments) and len(group) < CHUNK_MAX_SEGMENTS:
            # Force boundary on large time gaps
            gap = segments[j].start - group[-1].end
            if gap > CHUNK_GAP_THRESHOLD and len(group) >= CHUNK_MIN_SEGMENTS:
                break

            # Check word count
            combined_text = " ".join(s.text for s in group) + " " + segments[j].text
            if _word_count(combined_text) > CHUNK_MAX_WORDS and len(group) >= CHUNK_MIN_SEGMENTS:
                break

            group.append(segments[j])
            j += 1

        text = " ".join(s.text for s in group)
        chunks.append(Chunk(
            start_time=group[0].start,
            end_time=group[-1].end,
            text=text,
            chunk_index=chunk_index,
        ))
        chunk_index += 1

        # Advance with overlap
        advance = max(1, len(group) - CHUNK_OVERLAP)
        i += advance

    return chunks


def _word_count(text: str) -> int:
    return len(text.split())
