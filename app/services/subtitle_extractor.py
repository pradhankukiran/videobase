from __future__ import annotations

import asyncio
import json
import logging
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)


async def detect_subtitle_streams(video_path: Path) -> list[dict]:
    """Use ffprobe to find embedded subtitle streams."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-select_streams", "s",
        str(video_path),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        log.warning("ffprobe failed (rc=%d): %s", proc.returncode, stderr.decode())
        return []
    data = json.loads(stdout)
    streams = data.get("streams", [])
    log.info("Found %d subtitle stream(s) in %s", len(streams), video_path.name)
    return streams


async def extract_subtitle_track(
    video_path: Path, stream_index: int = 0, fmt: str = "srt",
) -> str | None:
    """Extract a subtitle track to a temp file, return the file path."""
    suffix = f".{fmt}"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.close()
    cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", str(video_path),
        "-map", f"0:s:{stream_index}",
        "-c:s", fmt if fmt == "srt" else "webvtt",
        tmp.name,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        log.warning("ffmpeg extract failed (rc=%d): %s", proc.returncode, stderr.decode())
        Path(tmp.name).unlink(missing_ok=True)
        return None
    content = Path(tmp.name).read_text(errors="replace")
    Path(tmp.name).unlink(missing_ok=True)
    return content if content.strip() else None


async def remux_mkv_to_mp4(mkv_path: Path) -> Path:
    """Remux MKV to MP4 (copy streams, no re-encode)."""
    mp4_path = mkv_path.with_suffix(".mp4")
    cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", str(mkv_path),
        "-c", "copy",
        "-movflags", "+faststart",
        str(mp4_path),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"Remux failed: {stderr.decode()}")
    mkv_path.unlink()
    return mp4_path
