#!/bin/bash

cd "$(dirname \"$0\")"

# UTF-8 safe Ollama check
if ! ps aux | grep -v grep | grep -q '[o]llama'; then
  echo \"❌ Ollama is not running.\"
  echo \"➡️  Open Terminal and run: ollama serve\"
  exit 1
fi

echo \"📦 Installing dependencies...\"
pip install --quiet fastapi uvicorn python-multipart

echo \"🚀 Starting FastAPI server at http://localhost:5000 ...\"
uvicorn image_renamer_app:app --reload --port 5000 &

sleep 2

echo \"🌐 Opening frontend...\"
open index.html
