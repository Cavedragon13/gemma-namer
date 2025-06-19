#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

# Optional: activate virtual environment
# source venv/bin/activate

# Check for ollama
if ! pgrep -x "ollama" > /dev/null; then
  echo "❌ Ollama is not running."
  echo "➡️  Start it with: ollama serve"
  exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies (if needed)..."
pip install --quiet fastapi uvicorn python-multipart

# Start FastAPI server in background
echo "🚀 Launching FastAPI server at http://localhost:5000 ..."
uvicorn app:app --reload --port 5000 &

# Give it a moment to spin up
sleep 2

# Open index.html in default browser
if [ -f "index.html" ]; then
  echo "🌐 Opening frontend in browser..."
  open index.html
else
  echo "⚠️  index.html not found in current directory."
fi
