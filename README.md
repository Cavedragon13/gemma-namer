# Gemma Namer - AI-Powered File Renaming

A sophisticated Electron desktop application that uses local Large Language Models (LLMs) to intelligently rename files based on their content. Supports multiple LLM backends and provides a clean, intuitive interface for bulk file operations.

## ✨ Features

- **AI-Powered Renaming**: Leverage local LLMs for intelligent file naming
- **Multiple LLM Backends**: Supports Ollama, Msty, and LM Studio
- **Bulk Operations**: Process multiple files simultaneously
- **Smart Content Analysis**: Analyzes file content to suggest meaningful names
- **Desktop Native**: Full Electron app with native OS integration
- **Privacy-First**: All processing happens locally (no cloud dependencies)

## 🛠️ Technologies

- **Framework**: Electron (Cross-platform desktop app)
- **Runtime**: Node.js with modern JavaScript
- **AI Integration**: Local LLM APIs (Ollama, Msty, LM Studio)
- **Frontend**: HTML, CSS, JavaScript (Electron renderer process)
- **Backend**: Node.js (Electron main process)
- **Architecture**: Secure IPC communication between processes

## 🚀 Getting Started

### Prerequisites

Install one of the supported LLM backends:

**Option 1: Ollama**
```bash
# Install Ollama
brew install ollama  # macOS
# or download from https://ollama.ai

# Pull a model (e.g., Llama 2)
ollama pull llama2
```

**Option 2: Msty**
- Download from https://msty.app

**Option 3: LM Studio**
- Download from https://lmstudio.ai

### Installation & Running

```bash
# Install dependencies
npm install

# Start the application
npm start

# For development
npm run dev
```

## 📁 Project Structure

```
gemma-namer/
├── main.js              # Electron main process
├── renderer.js          # Frontend application logic
├── preload.js          # Secure IPC bridge
├── index.html          # Main application interface
├── package.json        # Dependencies and scripts
├── package-lock.json   # Dependency lock file
├── node_modules/       # Installed packages
└── README.md          # This file
```

## 🎯 Key Features

### Smart File Analysis
- **Content Recognition**: Analyzes file types and content structure
- **Context Awareness**: Considers file location and existing naming patterns
- **Intelligent Suggestions**: Generates meaningful, descriptive names

### LLM Integration
- **Multiple Backends**: Seamless switching between LLM providers
- **Local Processing**: Privacy-focused with no external API calls
- **Customizable Prompts**: Tailor naming strategies for specific use cases

### User Experience
- **Drag & Drop**: Simple file selection interface
- **Batch Processing**: Handle large numbers of files efficiently
- **Preview Mode**: Review suggested names before applying
- **Undo Functionality**: Revert changes if needed

## 📊 Quality Score: 8/10

Professional desktop application with modern architecture:
- ✅ Clean Electron implementation with security best practices
- ✅ Multiple LLM backend support
- ✅ Professional desktop UI/UX
- ✅ Secure IPC communication
- ✅ Local processing (privacy-focused)
- ✅ Comprehensive file handling
- ⚠️ Requires local LLM setup
- ⚠️ Performance depends on local hardware

## 🔧 Configuration

### LLM Backend Setup

The application automatically detects available LLM backends:

1. **Ollama**: Runs on http://localhost:11434
2. **Msty**: Desktop application with API endpoint
3. **LM Studio**: Local server on configurable port

### Customization

- Modify prompts in `renderer.js` for different naming strategies
- Adjust file type handling in the main process
- Configure LLM parameters for speed vs. quality balance

## 🎯 Use Cases

Perfect for:
- **Media Organization**: Rename photos/videos with descriptive names
- **Document Management**: Organize files with meaningful titles
- **Code Organization**: Rename files based on content/function
- **Digital Asset Management**: Bulk rename design files, assets
- **Research Organization**: Organize papers, notes, references

## 🔒 Security & Privacy

- **Local Processing**: All AI processing happens on your machine
- **Secure IPC**: Electron security best practices with preload scripts
- **No Data Collection**: No telemetry or external data transmission
- **File Safety**: Non-destructive operations with undo functionality

## 💻 Platform Support

- **macOS**: Full native support
- **Windows**: Electron cross-platform compatibility
- **Linux**: Compatible with most distributions

## 🚀 Building for Distribution

```bash
# Build for current platform
npm run build

# Build for specific platforms
npm run build:mac
npm run build:win
npm run build:linux
```

## 📝 License

MIT License - feel free to use this application for personal or commercial projects.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional LLM backend integrations
- Enhanced content analysis algorithms
- Advanced renaming pattern templates
- UI/UX enhancements
- Performance optimizations
- Multi-language support
