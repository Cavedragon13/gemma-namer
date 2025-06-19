#!/usr/bin/env bash
#
# Local Image Renamer — one-click launcher
# ─────────────────────────────────────────────────────────────────────────────
# Requirements:
#   • ollama      https://ollama.ai
#   • exiftool    brew install exiftool
#   • Python ≥3.10 (activate your venv first)
# ---------------------------------------------------------------------------

set -e
export LC_ALL=C                   # avoid pgrep UTF-8 “illegal byte sequence”

cd "$(dirname "$0")"

PID_FILE=".server_pid"

# ────────────────────────────────────────────────────────────────────────────
# 0. If a previous server is still running, stop it
# ────────────────────────────────────────────────────────────────────────────
if [[ -f $PID_FILE ]]; then
  OLD_PID="$(cat "$PID_FILE")"
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "🛑  Stopping previous server (PID $OLD_PID)…"
    kill "$OLD_PID"
    # give uvicorn a moment to shut down gracefully
    sleep 2
  fi
  rm -f "$PID_FILE"
fi

# ────────────────────────────────────────────────────────────────────────────
# 1. Ensure Ollama daemon
# ────────────────────────────────────────────────────────────────────────────
if ! pgrep -x ollama >/dev/null ; then
  echo "🦙  Starting Ollama daemon (default port 11434)…"
  ollama serve >/dev/null 2>&1 &
  sleep 3
fi

# ────────────────────────────────────────────────────────────────────────────
# 2. Ensure the default vision model is loaded
# ────────────────────────────────────────────────────────────────────────────
DEF_MODEL="qwen2.5vl:latest"
[[ -f .last_model ]] && DEF_MODEL="$(cat .last_model)"

echo "🔍  Checking running models…"
if ! curl -s http://localhost:11434/api/tags | grep -q "\"$DEF_MODEL\"" ; then
  echo "🚀  Loading model $DEF_MODEL …"
  ollama run "$DEF_MODEL" >/dev/null 2>&1 &
  echo "$DEF_MODEL" > .last_model
  sleep 5
fi

# ────────────────────────────────────────────────────────────────────────────
# 3. Python dependencies
# ────────────────────────────────────────────────────────────────────────────
echo "📦  Installing Python packages…"
pip install --quiet -r requirements.txt

# ────────────────────────────────────────────────────────────────────────────
# 4. Launch FastAPI + Gradio
# ────────────────────────────────────────────────────────────────────────────
echo "🌐  Launching web UI at http://localhost:5000 …"
uvicorn renamer_backend:app --port 5000 --reload &
echo $! > "$PID_FILE"            # remember PID for next run
sleep 2

# macOS: open browser automatically
if command -v open >/dev/null ; then
  open "http://localhost:5000"
fi

echo "✅  Server running (PID $(cat "$PID_FILE")) — press Ctrl+C to exit this script, \
but the server will keep running until the next ./launcher.sh replaces it."