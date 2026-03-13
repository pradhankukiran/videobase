from pydantic import BaseModel


class Segment(BaseModel):
    start: float  # seconds
    end: float
    text: str


class Chunk(BaseModel):
    start_time: float
    end_time: float
    text: str
    chunk_index: int


class UploadResponse(BaseModel):
    video_id: str
    filename: str
    segment_count: int


class SearchResult(BaseModel):
    start_time: float
    end_time: float
    text: str
    score: float
