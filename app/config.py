from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = DATA_DIR / "videos"
CHROMA_DIR = DATA_DIR / "chroma"

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "BAAI/bge-m3"

# Chunking parameters
CHUNK_MIN_SEGMENTS = 2
CHUNK_MAX_SEGMENTS = 5
CHUNK_MAX_WORDS = 35
CHUNK_OVERLAP = 1
CHUNK_GAP_THRESHOLD = 4.0  # seconds — force boundary on silence gaps

SEARCH_TOP_K = 10
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
