import io
import re
import tempfile
from pathlib import Path

import pysrt
import webvtt

from app.models.schemas import Segment


def parse_srt(content: str) -> list[Segment]:
    """Parse SRT content string into segments."""
    tmp = tempfile.NamedTemporaryFile(suffix=".srt", mode="w", delete=False, encoding="utf-8")
    tmp.write(content)
    tmp.close()
    try:
        subs = pysrt.open(tmp.name, encoding="utf-8")
        segments = []
        for sub in subs:
            start = _srt_time_to_seconds(sub.start)
            end = _srt_time_to_seconds(sub.end)
            text = _clean_text(sub.text)
            if text:
                segments.append(Segment(start=start, end=end, text=text))
        return segments
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def parse_vtt(content: str) -> list[Segment]:
    """Parse VTT content string into segments."""
    tmp = tempfile.NamedTemporaryFile(suffix=".vtt", mode="w", delete=False, encoding="utf-8")
    tmp.write(content)
    tmp.close()
    try:
        segments = []
        for caption in webvtt.read(tmp.name):
            start = _vtt_timestamp_to_seconds(caption.start)
            end = _vtt_timestamp_to_seconds(caption.end)
            text = _clean_text(caption.text)
            if text:
                segments.append(Segment(start=start, end=end, text=text))
        return segments
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def parse_sbv(content: str) -> list[Segment]:
    """Parse SBV (YouTube subtitle) format."""
    segments = []
    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue
        time_line = lines[0]
        match = re.match(
            r"(\d+:\d+:\d+\.\d+),(\d+:\d+:\d+\.\d+)", time_line,
        )
        if not match:
            continue
        start = _sbv_timestamp_to_seconds(match.group(1))
        end = _sbv_timestamp_to_seconds(match.group(2))
        text = _clean_text(" ".join(lines[1:]))
        if text:
            segments.append(Segment(start=start, end=end, text=text))
    return segments


def parse_transcript(content: str, filename: str = "") -> list[Segment]:
    """Auto-detect format and parse."""
    lower = filename.lower()
    if lower.endswith(".vtt") or content.strip().startswith("WEBVTT"):
        return parse_vtt(content)
    if lower.endswith(".sbv"):
        return parse_sbv(content)
    # Default to SRT
    return parse_srt(content)


def _srt_time_to_seconds(t) -> float:
    return t.hours * 3600 + t.minutes * 60 + t.seconds + t.milliseconds / 1000


def _vtt_timestamp_to_seconds(ts: str) -> float:
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, rest = parts
    else:
        h = "0"
        m, rest = parts
    s, ms = rest.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def _sbv_timestamp_to_seconds(ts: str) -> float:
    h, m, rest = ts.split(":")
    s, ms = rest.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def _clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)  # strip HTML tags
    text = re.sub(r"\{[^}]+\}", "", text)  # strip ASS/SSA tags
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text
