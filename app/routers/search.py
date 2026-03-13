from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import SearchResult
from app.services.vector_store import search_video

router = APIRouter()


@router.get("/api/search", response_model=list[SearchResult])
async def search(
    video_id: str = Query(...),
    q: str = Query(..., min_length=1),
):
    results = search_video(video_id, q)
    if not results:
        return []
    return results
