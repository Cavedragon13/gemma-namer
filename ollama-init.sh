#!/bin/bash
#
# Ollama Model Initialization Script
# Downloads and sets up required AI models for Gemma Namer
#

set -e

echo "🦙 Initializing Ollama models for Gemma Namer..."

# Wait for Ollama service to be ready
echo "⏳ Waiting for Ollama service..."
while ! curl -sf http://localhost:11434/api/version > /dev/null; do
    echo "   Waiting for Ollama to start..."
    sleep 5
done

echo "✅ Ollama service is ready"

# Download default vision model
echo "📥 Downloading default vision model: qwen2.5vl:latest"
ollama pull qwen2.5vl:latest

# Download alternative models (optional)
echo "📥 Downloading alternative vision model: llava:latest"
ollama pull llava:latest

# Download lightweight text model for fallback
echo "📥 Downloading lightweight text model: gemma2:2b"
ollama pull gemma2:2b

# List installed models
echo "📋 Installed models:"
ollama list

echo "🎉 Ollama initialization complete!"
echo ""
echo "Available models for Gemma Namer:"
echo "  • qwen2.5vl:latest (default vision model)"
echo "  • llava:latest (alternative vision model)" 
echo "  • gemma2:2b (lightweight text model)"
echo ""
echo "To change the default model, create a .last_model file:"
echo "  echo 'llava:latest' > Local\ Image\ Renamer/.last_model"