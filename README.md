<div align="center">

# <img src="https://api.iconify.design/lucide:video.svg?color=%236366f1" width="32" height="32" alt="video icon" /> Videobase

**Semantic search for video content — find moments by meaning, not keywords.**

Upload a video with subtitles, search naturally, and jump straight to the result.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F61?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48L3N2Zz4=&logoColor=white)](https://www.trychroma.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## How It Works

1. **Upload** a video + subtitle file (SRT/VTT/SBV) — or a video with embedded subtitle tracks
2. **Index** — subtitles are chunked and embedded using [BGE-M3](https://huggingface.co/BAAI/bge-m3) multilingual embeddings
3. **Store** — embeddings are persisted in a local [ChromaDB](https://www.trychroma.com/) vector database
4. **Search** — queries are embedded and matched via cosine similarity against the index
5. **Jump** — click any result to seek the video player to that exact timestamp

> No external APIs, no cloud services — everything runs locally.

## Quick Start

```bash
git clone https://github.com/pradhankukiran/videobase.git
cd videobase
./run.sh
```

Open **http://localhost:8000**

The first run installs dependencies and downloads the embedding model (~2 GB). Subsequent starts are instant.

<details>
<summary><strong>Manual setup</strong></summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

</details>

### Prerequisites

- **Python 3.10+**
- **ffmpeg** — for extracting embedded subtitles and MKV remuxing

## Supported Formats

| Type | Formats |
|------|---------|
| **Video** | MP4, WebM, OGG, MKV (auto-remuxed to MP4) |
| **Subtitles** | SRT, VTT, SBV, or embedded tracks in the video file |

> Videos with burned-in (hardcoded) captions require a separate transcript file.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-2C2C2C?logo=uvicorn&logoColor=white) |
| **Embeddings** | ![Hugging Face](https://img.shields.io/badge/BGE--M3-FFD21E?logo=huggingface&logoColor=black) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white) |
| **Vector DB** | ![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F61?logoColor=white) |
| **Frontend** | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) |
| **Media** | ![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?logo=ffmpeg&logoColor=white) |

## Project Structure

```
videobase/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Paths, model, chunking params
│   ├── models/
│   │   └── schemas.py           # Pydantic data models
│   ├── routers/
│   │   ├── upload.py            # POST /api/upload
│   │   ├── search.py            # GET  /api/search
│   │   └── video.py             # GET  /api/video/{id}
│   └── services/
│       ├── embedder.py          # BGE-M3 model loading & encoding
│       ├── vector_store.py      # ChromaDB indexing & querying
│       ├── chunker.py           # Sliding-window subtitle chunking
│       ├── transcript_parser.py # SRT / VTT / SBV parsing
│       └── subtitle_extractor.py# ffmpeg subtitle extraction & remux
├── static/
│   ├── index.html               # Single-page frontend
│   ├── app.js                   # UI logic, search, video player
│   └── style.css                # Custom styles + Tailwind
├── run.sh                       # One-command setup & run
└── requirements.txt
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload video + optional transcript, returns `video_id` |
| `GET` | `/api/search?video_id=<id>&q=<query>` | Semantic search, returns ranked results with timestamps |
| `GET` | `/api/video/{video_id}` | Stream video file |

## License

[MIT](LICENSE)
