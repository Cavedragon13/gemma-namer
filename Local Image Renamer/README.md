# Local Image Renamer

🤖 **AI-powered image toolkit: Generate, rename, and organize**

A comprehensive web application that both generates new images and intelligently renames/organizes existing ones. Create images with DALL-E or Flux.1, then automatically organize them using local AI vision models.

![Local Image Renamer](static/Seed_13_logo.jpg)

## ✨ Features

### 🎨 Image Generation
- **DALL-E Integration**: Generate images using OpenAI's DALL-E models
- **Flux.1 Support**: Alternative image generation via Flux.1 API
- **Image Editing**: Edit existing images with masks and prompts
- **Batch Generation**: Process multiple prompts from files

### 🧠 AI-Powered Organization
- **Smart Naming**: Uses local vision models (Ollama) to generate descriptive filenames
- **Intelligent Grouping**: Automatically groups similar images into folders
- **EXIF Metadata**: Adds keywords and captions to image metadata
- **Processing History**: SQLite database tracks all operations

### 🌐 User Experience
- **Dual Interface**: Both Gradio UI and REST API endpoints
- **Drag-and-Drop**: Easy bulk uploads and file management
- **Privacy Options**: Local processing (Ollama) or cloud APIs (OpenAI/Flux)
- **Auto Cleanup**: Temporary files cleaned up automatically

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with pip
- **Ollama** - Local AI model server ([Download](https://ollama.ai))
- **exiftool** - Image metadata editor
  - macOS: `brew install exiftool`
  - Ubuntu: `apt-get install libimage-exiftool-perl`

#### Optional API Keys
- **OpenAI API Key** - For DALL-E image generation
- **Flux API Key** - For Flux.1 image generation

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd local-image-renamer
   pip install -r requirements.txt
   ```

2. **Install Ollama and vision model**:
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Download default vision model
   ollama pull qwen2.5vl:latest
   ```

3. **Configure API keys** (optional):
   ```bash
   # Create .env file for API keys
   echo "OPENAI_API_KEY=your-openai-key-here" > .env
   echo "FLUX_API_KEY=your-flux-key-here" >> .env
   ```

4. **Launch the application**:
   ```bash
   ./launcher.sh
   ```

The web interface will open automatically at `http://localhost:5000`

## 💡 How It Works

### 🎨 Image Generation Workflow
1. **Create Prompts**: Upload text files with image prompts
2. **Generate Images**: Choose DALL-E or Flux.1 for image generation
3. **Auto-Process**: Generated images can be automatically renamed and organized

### 🧠 Image Organization Workflow
1. **Upload Images**: Drag and drop images or folders into the web interface
2. **AI Analysis**: Each image is analyzed by a local vision model to generate descriptions
3. **Smart Naming**: Filenames are created from the AI descriptions (sanitized and shortened)
4. **Intelligent Grouping**: Similar images are grouped together using fuzzy matching
5. **Organization**: Groups with 3+ images get folders; smaller groups go to "one-offs"
6. **Metadata Enhancement**: EXIF data is enriched with keywords and captions

## 📂 Output Structure

```
project/
├── output/               # Organized renamed images
│   ├── landscape_photography/
│   │   ├── mountain_sunset_landscape_01.jpg
│   │   └── mountain_sunset_landscape_02.jpg
│   └── one-offs/
│       └── abstract_art_piece.jpg
├── generated/            # AI-generated images
│   ├── dall-e_session_001/
│   │   ├── img_001.png
│   │   └── img_002.png
│   └── flux_session_002.png
└── files.db             # Processing history
```

## ⚙️ Configuration

### Change AI Model

```bash
# Use a different vision model
echo "llava:latest" > .last_model
./launcher.sh
```

### Custom Processing

Edit configuration in `renamer_backend.py`:

```python
MODEL_NAME = "qwen2.5vl:latest"  # AI model
CAPTION_PROMPT = "Describe the image..."  # Custom prompt
OUT_DIR = Path("output")  # Output directory
```

## 🛠️ Development

### Manual Startup

```bash
# Start Ollama daemon
ollama serve

# Start web application
uvicorn renamer_backend:app --port 5000 --reload
```

### Database Operations

```bash
# View processing history
sqlite3 files.db "SELECT orig_path, caption, keywords FROM images LIMIT 10;"

# Reset database
rm files.db
```

## 📋 API Endpoints

### Core Interface
- `GET /` - Redirects to Gradio interface
- `GET /gradio` - Gradio web interface
- `GET /static/*` - Static assets

### Image Processing
- `POST /upload` - Upload images for renaming/organization

### Image Generation
- `POST /generate` - Generate images from prompts using DALL-E
- `POST /generate-flux` - Generate images using Flux.1 API
- `POST /edit-image` - Edit images with masks and prompts

## 🔧 Troubleshooting

### Common Issues

**Ollama not responding**:
```bash
ollama serve  # Ensure daemon is running
ollama list   # Check installed models
```

**exiftool not found**:
```bash
# macOS
brew install exiftool

# Ubuntu/Debian
sudo apt-get install libimage-exiftool-perl
```

**API key errors**:
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $FLUX_API_KEY

# Verify .env file
cat .env
```

**Port 5000 in use**:
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or use different port
uvicorn renamer_backend:app --port 5001
```

## 🏗️ Architecture

- **Backend**: FastAPI with async processing
- **Frontend**: Gradio web interface
- **AI Models**: Ollama (local inference)
- **Database**: SQLite for metadata storage
- **Image Processing**: PIL + exiftool

## 📄 License

© 2024 Seed 13 — All rights reserved.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Need help?** Open an issue or check the [troubleshooting guide](#-troubleshooting).