from pathlib import Path

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

from app.config import VIDEOS_DIR

router = APIRouter()


@router.get("/api/video/{video_id}")
async def serve_video(video_id: str):
    # Find the video file (could be .mp4, .webm, etc.)
    matches = list(VIDEOS_DIR.glob(f"{video_id}.*"))
    if not matches:
        raise HTTPException(404, "Video not found")
    video_path = matches[0]

    media_types = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".ogg": "video/ogg",
    }
    content_type = media_types.get(video_path.suffix.lower(), "video/mp4")

    return FileResponse(
        path=video_path,
        media_type=content_type,
        filename=video_path.name,
    )
