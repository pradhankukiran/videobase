#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Check ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "Error: ffmpeg is required but not installed."
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS:         brew install ffmpeg"
    echo "  Fedora:        sudo dnf install ffmpeg"
    exit 1
fi

# Create venv if missing
if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install deps if needed
if [ ! -f .venv/.installed ]; then
    echo "Installing dependencies (this may take a few minutes)..."
    pip install --upgrade pip -q
    pip install torch --index-url https://download.pytorch.org/whl/cpu -q
    pip install -r requirements.txt -q
    touch .venv/.installed
    echo "Done."
fi

# Create data dirs
mkdir -p data/videos data/chroma

echo ""
echo "Starting Videobase at http://localhost:8000"
echo "Press Ctrl+C to stop."
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000
