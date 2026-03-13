# Videobase

Search through video content semantically. Upload a video with a transcript (SRT/VTT/SBV), then search by meaning — not just keywords. Click a result to jump to that moment in the video.

![Python](https://img.shields.io/badge/python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## How it works

1. Upload a video + subtitle file (or a video with embedded subtitle tracks)
2. Subtitles are chunked and embedded using [BGE-M3](https://huggingface.co/BAAI/bge-m3)
3. Embeddings are stored in [ChromaDB](https://www.trychroma.com/) (local, no external services)
4. Search queries are embedded and matched against the index
5. Click any result to jump the video player to that timestamp

## Requirements

- Python 3.10+
- ffmpeg (for extracting embedded subtitles and MKV remuxing)

## Quick start

```bash
git clone https://github.com/pradhankukiran/videobase.git
cd videobase
./run.sh
```

Open http://localhost:8000

The first run installs dependencies and downloads the embedding model (~2GB total). Subsequent starts are instant.

### Manual setup

If you prefer not to use the script:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Supported formats

- **Video**: MP4, WebM, OGG, MKV (auto-remuxed to MP4)
- **Transcripts**: SRT, VTT, SBV — or embedded subtitle tracks in the video file

If your video has burned-in (hardcoded) captions, you'll need to provide a separate transcript file.

## Tech stack

- **FastAPI** — API + static file serving
- **BGE-M3** via sentence-transformers — multilingual semantic embeddings
- **ChromaDB** — local vector database, no external services
- **Vanilla JS + Tailwind CDN** — no build step
