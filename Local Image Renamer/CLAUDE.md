# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Local Image Renamer is a Python-based web application that uses AI vision models to automatically rename and organize images in bulk. It combines FastAPI backend with a Gradio web UI for easy file uploads and processing.

## Architecture

### Core Components

- **renamer_backend.py**: Main FastAPI application with embedded Gradio UI
  - Handles file uploads and processing
  - Integrates with Ollama for AI-powered image captioning
  - Uses SQLite database for metadata storage
  - Groups similar images based on fuzzy string matching
- **launcher.sh**: One-click startup script that manages dependencies
- **files.db**: SQLite database storing image metadata and processing history

### Key Dependencies

- **Ollama**: Local AI model server (required for image captioning)
- **exiftool**: Command-line metadata editor for images
- **FastAPI + Uvicorn**: Web server framework
- **Gradio**: Web UI for file uploads
- **PIL**: Image processing
- **rapidfuzz**: Fuzzy string matching for grouping similar images

## Commands

### Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies
brew install exiftool  # macOS
# or apt-get install libimage-exiftool-perl  # Ubuntu

# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve  # Start daemon
ollama pull qwen2.5vl:latest  # Download default vision model
```

### Running the Application

```bash
# One-click launcher (recommended)
./launcher.sh

# Manual startup
ollama serve  # Start Ollama daemon in separate terminal
uvicorn renamer_backend:app --port 5000 --reload
```

### Configuration

```bash
# Change AI model (create .last_model file)
echo "llava:latest" > .last_model

# Default model locations
echo "qwen2.5vl:latest" > .last_model  # Default vision model
```

### Database Operations

```bash
# Check processing history
sqlite3 files.db "SELECT * FROM images LIMIT 10;"

# Clear database
rm files.db  # Will be recreated on next run
```

## Processing Pipeline

1. **Upload**: Images uploaded via Gradio web interface
2. **Caption**: Each image sent to Ollama vision model for description
3. **SEO Tags**: Secondary AI call generates keywords and summary
4. **Naming**: Filename generated from first part of caption (sanitized)
5. **Grouping**: Similar filenames grouped using fuzzy matching (85% threshold)
6. **Organization**: 
   - Groups with 3+ images get their own folders
   - Smaller groups moved to "one-offs" folder
7. **Metadata**: EXIF data written with keywords and captions
8. **Database**: Processing results stored in SQLite

## Key Configuration Variables

```python
OLLAMA_URL = "http://localhost:11434"          # Ollama server endpoint
MODEL_NAME = "qwen2.5vl:latest"               # Default vision model
CAPTION_PROMPT = "Describe the image..."       # AI captioning prompt
OUT_DIR = Path("output")                       # Processed images output
DB = Path("files.db")                          # SQLite database location
```

## File Structure

- `output/`: Organized, renamed images with metadata
- `static/`: Web assets (logo, etc.)
- `Deprecated/`: Legacy versions and old implementations
- `.last_model`: Current Ollama model selection
- `.server_pid`: Process ID for running server (launcher.sh)

## Development Notes

### Error Handling
- Graceful fallback for AI model failures
- JSON parsing fallback for malformed SEO responses
- Database connection management with proper cleanup

### Performance Considerations
- Async/await for AI model calls
- Chunked file uploads (1MB chunks)
- Background task processing for large batches
- Connection timeouts: 120s for captioning, 60s for SEO

### Security
- File type validation (images only)
- Path sanitization for generated filenames
- No external network access (uses local Ollama)