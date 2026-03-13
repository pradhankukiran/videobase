from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import MAX_UPLOAD_SIZE, VIDEOS_DIR
from app.models.schemas import UploadResponse
from app.services.chunker import chunk_segments
from app.services.subtitle_extractor import (
    detect_subtitle_streams,
    extract_subtitle_track,
    remux_mkv_to_mp4,
)
from app.services.transcript_parser import parse_transcript
from app.services.vector_store import index_video

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/upload", response_model=UploadResponse)
async def upload_video(
    video: UploadFile = File(...),
    transcript: UploadFile | None = File(None),
):
    video_id = uuid.uuid4().hex[:12]
    original_name = video.filename or "video"

    # Save video to disk
    suffix = Path(original_name).suffix.lower()
    video_path = VIDEOS_DIR / f"{video_id}{suffix}"
    size = 0
    with open(video_path, "wb") as f:
        while chunk := await video.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_SIZE:
                video_path.unlink(missing_ok=True)
                raise HTTPException(413, "File too large (max 2GB)")
            f.write(chunk)

    # Remux MKV to MP4
    if suffix == ".mkv":
        try:
            video_path = await remux_mkv_to_mp4(video_path)
        except RuntimeError as e:
            video_path.unlink(missing_ok=True)
            raise HTTPException(500, f"MKV remux failed: {e}")

    # Get transcript content
    transcript_content: str | None = None
    transcript_filename = ""

    has_transcript_file = (
        transcript is not None
        and transcript.filename
        and transcript.size is not None
        and transcript.size > 0
    )
    if has_transcript_file:
        raw = await transcript.read()
        if raw:
            transcript_content = raw.decode("utf-8", errors="replace")
            transcript_filename = transcript.filename

    if not transcript_content:
        # Try extracting embedded subtitles
        streams = await detect_subtitle_streams(video_path)
        if streams:
            transcript_content = await extract_subtitle_track(video_path, stream_index=0)
            transcript_filename = "extracted.srt"

    if not transcript_content:
        video_path.unlink(missing_ok=True)
        raise HTTPException(
            400,
            "No subtitle tracks found in this video. "
            "Please upload a transcript file (SRT, VTT, or SBV) alongside the video.",
        )

    # Parse → chunk → embed → index
    segments = parse_transcript(transcript_content, transcript_filename)
    if not segments:
        video_path.unlink(missing_ok=True)
        raise HTTPException(400, "Could not parse any subtitle segments from the transcript.")

    chunks = chunk_segments(segments)
    index_video(video_id, chunks)

    return UploadResponse(
        video_id=video_id,
        filename=video_path.name,
        segment_count=len(chunks),
    )
