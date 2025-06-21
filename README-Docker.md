# Gemma Namer - Docker Setup

🐳 **Run Gemma Namer with Docker for easy deployment and consistent environments**

This guide covers Docker setup for both the Python Local Image Renamer web app and the Electron desktop application.

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- At least **8GB RAM** (for Ollama AI models)
- **10GB free disk space** (for models and containers)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd gemma-namer
```

### 2. Start the Web Application

```bash
# Start Python web app with Ollama
docker-compose up -d

# Initialize AI models (first time only)
docker-compose exec ollama bash -c "/app/ollama-init.sh"
```

### 3. Access the Application

- **Web Interface**: http://localhost:5000
- **Ollama API**: http://localhost:11434

## 📋 Available Services

### Core Services (Default)

```bash
# Start web application only
docker-compose up -d ollama image-renamer
```

- `ollama` - Local AI model server (port 11434)
- `image-renamer` - Python web application (port 5000)

### Desktop Application (Optional)

```bash
# Start with desktop app (VNC access)
docker-compose --profile desktop up -d
```

- `electron-app` - Electron desktop app via VNC (port 6080)
- Access via web browser: http://localhost:6080

## 🛠️ Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```bash
# .env file
OLLAMA_URL=http://ollama:11434
MODEL_NAME=qwen2.5vl:latest
GRADIO_SERVER_PORT=5000
VNC_PASSWORD=gemma123
RESOLUTION=1024x768

# Optional API keys for image generation
OPENAI_API_KEY=your-openai-key
FLUX_API_KEY=your-flux-key
```

### Custom Models

```bash
# Use different AI model
echo "llava:latest" > "Local Image Renamer/.last_model"
docker-compose restart image-renamer

# Download additional models
docker-compose exec ollama ollama pull codellama:latest
```

### Persistent Data

Data is automatically persisted in Docker volumes:

- `ollama_data` - AI models and Ollama configuration
- `image_db` - SQLite database with processing history
- `electron_data` - Desktop app user data

## 📁 Directory Structure

```bash
gemma-namer/
├── docker-compose.yml          # Main orchestration
├── Dockerfile.electron         # Desktop app container
├── .dockerignore              # Docker ignore patterns
├── ollama-init.sh             # Model initialization
├── uploads/                   # Input images (mounted)
├── output/                    # Processed images (mounted)
└── Local Image Renamer/
    ├── Dockerfile             # Web app container
    ├── docker-entrypoint.sh   # Container startup script
    └── ...
```

## 🔧 Common Commands

### Development

```bash
# Build containers from source
docker-compose build

# View logs
docker-compose logs -f image-renamer
docker-compose logs -f ollama

# Shell access
docker-compose exec image-renamer bash
docker-compose exec ollama bash

# Restart services
docker-compose restart
```

### Production

```bash
# Run in background (production)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Model Management

```bash
# List installed models
docker-compose exec ollama ollama list

# Pull new model
docker-compose exec ollama ollama pull llava:latest

# Check model status
docker-compose exec ollama ollama ps
```

## 🏥 Health Monitoring

### Service Status

```bash
# Check all services
docker-compose ps

# Health check endpoints
curl http://localhost:5000/health    # Web app
curl http://localhost:11434/api/version  # Ollama
```

### Resource Usage

```bash
# Monitor resource usage
docker stats

# View container logs
docker-compose logs --tail=50 -f image-renamer
```

## 📊 Performance Tuning

### Memory Optimization

```bash
# Limit container memory (in docker-compose.yml)
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 4G
  image-renamer:
    deploy:
      resources:
        limits:
          memory: 1G
```

### GPU Support (Optional)

For NVIDIA GPU acceleration:

```yaml
# Add to ollama service in docker-compose.yml
services:
  ollama:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

## 🐛 Troubleshooting

### Common Issues

**Ollama model download fails:**
```bash
# Manual model download
docker-compose exec ollama bash
ollama pull qwen2.5vl:latest
```

**Port already in use:**
```bash
# Change ports in docker-compose.yml
ports:
  - "5001:5000"  # Web app
  - "11435:11434"  # Ollama
```

**Permission denied errors:**
```bash
# Fix file permissions
sudo chown -R $(id -u):$(id -g) uploads/ output/
```

**Container fails to start:**
```bash
# Check logs
docker-compose logs ollama
docker-compose logs image-renamer

# Reset everything
docker-compose down -v
docker system prune -f
```

### Resource Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB (8GB recommended)
- Disk: 5GB free space

**Recommended for Best Performance:**
- CPU: 4+ cores
- RAM: 8GB+ (16GB with multiple models)
- Disk: 20GB+ SSD storage
- GPU: NVIDIA GPU with 6GB+ VRAM (optional)

## 🔒 Security Considerations

### Network Security

```bash
# Run on custom network
docker network create gemma-network
# Update docker-compose.yml accordingly
```

### Data Privacy

- All AI processing happens locally (no external API calls)
- Images and metadata stay within Docker containers
- SQLite database contains processing history

### Access Control

```bash
# Change VNC password
export VNC_PASSWORD=your-secure-password
docker-compose up -d
```

## 🚀 Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml gemma-namer
```

### Kubernetes

See `k8s/` directory for Kubernetes manifests (if available).

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale web app instances
docker-compose up -d --scale image-renamer=3
```

### Load Balancing

Add nginx or traefik reverse proxy for multiple instances.

---

**Need help?** Check the [main README](README.md) or open an issue for Docker-specific problems.