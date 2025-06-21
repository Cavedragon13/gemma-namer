#!/bin/bash
#
# Docker entrypoint script for Local Image Renamer
# Handles initialization and health checks
#

set -e

echo "🐳 Starting Local Image Renamer container..."

# Wait for Ollama service to be ready
echo "⏳ Waiting for Ollama service at $OLLAMA_URL..."
until curl -sf "$OLLAMA_URL/api/version" > /dev/null 2>&1; do
    echo "   Ollama not ready, waiting 5 seconds..."
    sleep 5
done

echo "✅ Ollama service is ready"

# Check if default model is available
DEFAULT_MODEL="${MODEL_NAME:-qwen2.5vl:latest}"
echo "🔍 Checking for model: $DEFAULT_MODEL"

# Try to load the model if not already loaded
if ! curl -sf "$OLLAMA_URL/api/tags" | grep -q "\"$DEFAULT_MODEL\""; then
    echo "📥 Model not found, attempting to pull: $DEFAULT_MODEL"
    curl -X POST "$OLLAMA_URL/api/pull" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$DEFAULT_MODEL\"}" || {
        echo "⚠️  Warning: Could not pull model $DEFAULT_MODEL"
        echo "   The application will still start but may not function properly"
        echo "   until a vision model is available in Ollama"
    }
fi

# Create output directories if they don't exist
mkdir -p /app/output /app/generated /app/uploads

# Initialize database if it doesn't exist
if [ ! -f /app/files.db ]; then
    echo "🗄️  Initializing database..."
    python3 -c "
import sqlite3
conn = sqlite3.connect('/app/files.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        orig_path TEXT NOT NULL,
        new_path TEXT,
        caption TEXT,
        keywords TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()
print('Database initialized successfully')
"
fi

# Add health check endpoint
echo "🏥 Adding health check endpoint..."
cat >> /app/renamer_backend.py << 'EOF'

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    try:
        # Check Ollama connection
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/version")
            ollama_status = response.status_code == 200
        
        return {
            "status": "healthy",
            "ollama_connected": ollama_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
EOF

echo "🚀 Starting application..."

# Start the application
exec "$@"