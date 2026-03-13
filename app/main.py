from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR
from app.services.embedder import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load embedding model at startup
    load_model()
    yield


app = FastAPI(title="Videobase", lifespan=lifespan)

# Register routers
from app.routers import search, upload, video

app.include_router(upload.router)
app.include_router(search.router)
app.include_router(video.router)

# Serve static files (index.html, app.js, style.css)
app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")
