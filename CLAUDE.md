# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Gemma Namer is an Electron desktop application that uses local Large Language Models (LLMs) to intelligently rename files based on their content. The repository contains both the Electron app and a separate Python-based "Local Image Renamer" web application for AI-powered image processing and organization.

## Commands

### Electron Desktop App (Main Project)

```bash
# Install dependencies
npm install

# Start development
npm start

# Build for distribution
npm run build
npm run build:mac
npm run build:win  
npm run build:linux
```

### Docker Deployment

```bash
# Start web application with Ollama
docker-compose up -d

# Initialize AI models (first time)
docker-compose exec ollama bash -c "./ollama-init.sh"

# Start with desktop app (VNC access)
docker-compose --profile desktop up -d

# Access web interface: http://localhost:5000
# Access VNC desktop: http://localhost:6080
```

### Local Image Renamer (Python Web App)

```bash
# Install Python dependencies
pip install -r "Local Image Renamer/requirements.txt"

# Install system dependencies
brew install exiftool  # macOS
# apt-get install libimage-exiftool-perl  # Ubuntu

# Setup Ollama (local AI server)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull qwen2.5vl:latest

# Start the web application
cd "Local Image Renamer"
./launcher.sh
# OR manually: uvicorn renamer_backend:app --port 5000 --reload
```

## Architecture Overview

### Electron Desktop App Structure

- **main.js**: Electron main process with IPC handlers for folder selection and file operations
- **renderer.js**: Frontend logic for the folder picker interface
- **preload.js**: Secure IPC bridge using contextBridge pattern
- **index.html**: Main UI with clean, branded styling (red/silver theme)
- **package.json**: Defines Electron app with axios dependency for LLM API calls

### Security Architecture

The Electron app follows security best practices:
- Uses `preload.js` with `contextBridge` for secure IPC communication
- Exposes limited API surface (`gemmaAPI.pickFolder`, `gemmaAPI.getFiles`)
- However, currently has `nodeIntegration: true` and `contextIsolation: false` which should be addressed for production

### LLM Integration Pattern

The application is designed to work with multiple local LLM backends:
- **Ollama**: Default backend on http://localhost:11434
- **Msty**: Desktop application with API endpoint
- **LM Studio**: Local server on configurable port

### File Processing Workflow

1. User selects folder via native OS dialog
2. Recursive file discovery across subdirectories
3. Files sent to local LLM for content analysis
4. LLM generates descriptive names based on file content
5. User previews and applies renaming operations

## Key Technologies

### Desktop App Stack
- **Electron 29.2.0**: Cross-platform desktop framework
- **Node.js**: Backend processing with filesystem operations
- **Vanilla JavaScript**: No frontend frameworks, pure DOM manipulation
- **Native OS Integration**: File dialogs, keyboard shortcuts (Cmd/Ctrl+Shift+G)

### Python Web App Stack (Local Image Renamer)
- **FastAPI**: Async web framework with REST API
- **Gradio**: Web UI for file uploads and processing
- **Ollama**: Local AI inference server
- **SQLite**: Metadata storage and processing history
- **PIL + exiftool**: Image processing and metadata manipulation
- **rapidfuzz**: Fuzzy string matching for intelligent file grouping

## Project Structure

```
gemma-namer/
├── main.js              # Electron main process
├── renderer.js          # Frontend application logic  
├── preload.js          # Secure IPC bridge
├── index.html          # Main UI
├── package.json        # Node.js dependencies
├── README.md           # Desktop app documentation
└── Local Image Renamer/ # Separate Python web application
    ├── renamer_backend.py    # FastAPI backend with Gradio UI
    ├── launcher.sh          # One-click startup script
    ├── requirements.txt     # Python dependencies
    ├── files.db            # SQLite processing history
    └── static/             # Web assets
```

## Development Patterns

### IPC Communication Pattern
The Electron app uses a secure IPC pattern:
```javascript
// preload.js - Secure bridge
contextBridge.exposeInMainWorld('gemmaAPI', {
  pickFolder: () => ipcRenderer.invoke('pick-folder'),
  getFiles: (folderPath) => ipcRenderer.invoke('get-files', folderPath),
});

// main.js - Handler implementation  
ipcMain.handle('pick-folder', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});
```

### File Discovery Algorithm
```javascript
function getAllFiles(dir, files = []) {
  fs.readdirSync(dir).forEach(file => {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      getAllFiles(fullPath, files);  // Recursive
    } else {
      files.push(fullPath);
    }
  });
  return files;
}
```

### UI Styling Conventions
- **Color Scheme**: Deep red (#b71c1c) primary with silver/gray accents
- **Typography**: Segoe UI system font stack
- **Layout**: Centered containers with subtle shadows and rounded corners
- **Responsive**: Uses relative units and flexible layouts

## Configuration

### LLM Backend Detection
The application automatically detects available LLM backends by testing endpoints:
1. Ollama: http://localhost:11434
2. Msty: Desktop app API endpoint
3. LM Studio: Configurable port (typically 1234)

### Customization Points
- **Prompts**: Modify in renderer.js for different naming strategies
- **File Filters**: Adjust file type handling in main process
- **LLM Parameters**: Configure for speed vs quality balance
- **UI Theme**: Colors and styling in index.html `<style>` block

## Performance Considerations

- **File Processing**: Recursive directory traversal for large folder structures
- **Memory Management**: File lists stored in memory during processing
- **LLM Calls**: Sequential API calls to local models (could be parallelized)
- **UI Responsiveness**: Synchronous file operations may block UI

## Docker Architecture

### Container Services
- **ollama**: Local AI model server with persistent model storage
- **image-renamer**: Python FastAPI web application with Gradio UI
- **electron-app**: Desktop application accessible via VNC (optional)

### Data Persistence
- `ollama_data`: AI models and configuration
- `image_db`: SQLite processing history
- `electron_data`: Desktop app user data

### Networking
All services communicate via Docker bridge network with health checks and automatic restarts.

## Development Workflow

### Local Development
1. **Setup**: Install Node.js dependencies and chosen LLM backend
2. **Development**: Use `npm start` for live development with DevTools
3. **Testing**: Manual testing with various folder structures and file types
4. **Building**: Use electron-builder for cross-platform distribution
5. **Distribution**: DMG (macOS), MSI (Windows), AppImage (Linux)

### Docker Development
1. **Setup**: `docker-compose up -d` starts all services
2. **Development**: Edit code, containers auto-restart on changes
3. **Testing**: Access web UI at localhost:5000, VNC at localhost:6080
4. **Debugging**: `docker-compose logs -f` for real-time logging
5. **Distribution**: Build production images with `docker-compose build`