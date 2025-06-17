# ClipForge Installation Guide 🎬

Complete installation and setup guide for ClipForge AI Video Editor.

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Required for AI model downloads and API calls

### Supported Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+, CentOS 7+)

## Pre-Installation Setup

### 1. Install Python
Download Python from [python.org](https://python.org) or use a package manager:

```bash
# Windows (using Chocolatey)
choco install python

# macOS (using Homebrew)
brew install python

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip

# Linux (CentOS/RHEL)
sudo yum install python3 python3-pip
```

### 2. Install FFmpeg
FFmpeg is required for video processing:

#### Windows
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH environment variable

Or use package manager:
```bash
# Windows (using Chocolatey)
choco install ffmpeg

# Windows (using Scoop)
scoop install ffmpeg
```

#### macOS
```bash
# Using Homebrew
brew install ffmpeg
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Or compile from source for latest version
```

### 3. Verify FFmpeg Installation
```bash
ffmpeg -version
```
You should see version information if installed correctly.

## ClipForge Installation

### Method 1: Quick Install (Recommended)
```bash
# Clone the repository
git clone https://github.com/noahwilliamshaffer/AiVideoEditor.git
cd AiVideoEditor

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### Method 2: Development Install
```bash
# Clone and install in development mode
git clone https://github.com/noahwilliamshaffer/AiVideoEditor.git
cd AiVideoEditor

# Create virtual environment (recommended)
python -m venv clipforge_env

# Activate virtual environment
# Windows:
clipforge_env\Scripts\activate
# macOS/Linux:
source clipforge_env/bin/activate

# Install with development dependencies
pip install -e .[dev]

# Install pre-commit hooks (optional)
pre-commit install
```

## Configuration

### 1. API Keys Setup
Create a `.env` file in the project root:

```bash
# Copy example configuration
cp .env.example .env
```

Edit `.env` with your API keys:
```env
# OpenAI API Key (required for GPT features)
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration (optional - for cloud sync)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Application Settings
DEBUG=True
MAX_FILE_SIZE_MB=500
WHISPER_MODEL=base
WHISPER_DEVICE=cpu
```

### 2. Get OpenAI API Key
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Add it to your `.env` file

### 3. GPU Setup (Optional)
For faster processing with CUDA-enabled GPUs:

```bash
# Install PyTorch with CUDA support
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update configuration
# In .env file:
WHISPER_DEVICE=cuda
```

## Running ClipForge

### Option 1: Using Run Script (Recommended)
```bash
python run.py
```
This will:
- Check dependencies
- Verify FFmpeg installation
- Start the Streamlit application
- Open your browser automatically

### Option 2: Direct Streamlit Launch
```bash
streamlit run app.py
```

### Option 3: Command Line Interface
```bash
# Future: CLI interface for batch processing
python -m clipforge --help
```

## First Run

1. **Open your browser** to `http://localhost:8501`
2. **Upload a video** using the drag-and-drop interface
3. **Select features** (Auto Captions, Meme Mode, B-roll)
4. **Configure settings** in the sidebar
5. **Click "Process Video"** and wait for completion
6. **Download** your processed video

## Troubleshooting

### Common Issues

#### "FFmpeg not found"
```bash
# Check if FFmpeg is in PATH
ffmpeg -version

# If not found, reinstall or add to PATH
# Windows: Add FFmpeg bin folder to PATH environment variable
# macOS/Linux: Install via package manager
```

#### "OpenAI API key not found"
- Ensure `.env` file exists in project root
- Check that `OPENAI_API_KEY` is set correctly
- Verify API key is valid on OpenAI platform

#### "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific missing package
pip install package_name
```

#### "Permission denied" errors
```bash
# Ensure proper permissions
chmod +x run.py

# Or run with explicit python
python run.py
```

#### Memory errors with large videos
- Reduce video size before processing
- Use smaller Whisper model (`tiny` instead of `base`)
- Close other applications to free RAM
- Consider upgrading hardware

### Performance Optimization

#### For Better Speed
- Use `tiny` or `small` Whisper models
- Enable GPU acceleration (CUDA)
- Process shorter video segments
- Use SSD storage for temp files

#### For Better Quality
- Use `large` Whisper model
- Increase video bitrate settings
- Use higher resolution source videos
- Enable quality mode in settings

## Development Setup

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_video_processor.py

# Run with coverage
python -m pytest --cov=src
```

### Code Formatting
```bash
# Format code with black
black .

# Check style with flake8
flake8 src tests

# Type checking with mypy
mypy src
```

### Building Documentation
```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme

# Build documentation
cd docs
make html
```

## Docker Installation (Alternative)

### Using Docker
```bash
# Build Docker image
docker build -t clipforge .

# Run container
docker run -p 8501:8501 -v $(pwd)/output:/app/output clipforge
```

### Using Docker Compose
```bash
# Start all services
docker-compose up

# Access application at http://localhost:8501
```

## Advanced Configuration

### Custom Models
```bash
# Use custom Whisper model
export WHISPER_MODEL=medium

# Use custom output directory
export OUTPUT_DIR=/path/to/outputs
```

### Database Configuration
```bash
# Use custom database location
export DATABASE_URL=sqlite:///custom/path/clipforge.db

# Or use PostgreSQL
export DATABASE_URL=postgresql://user:pass@localhost/clipforge
```

### Logging Configuration
```bash
# Enable debug logging
export DEBUG=True

# Custom log level
export LOG_LEVEL=DEBUG

# Custom log directory
export LOG_DIR=/path/to/logs
```

## Getting Help

### Support Channels
- **Documentation**: [GitHub Wiki](https://github.com/noahwilliamshaffer/AiVideoEditor/wiki)
- **Issues**: [GitHub Issues](https://github.com/noahwilliamshaffer/AiVideoEditor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/noahwilliamshaffer/AiVideoEditor/discussions)
- **Email**: support@clipforge.ai

### Before Reporting Issues
1. Check this installation guide
2. Search existing GitHub issues
3. Try with a small test video
4. Include system information and error logs

### System Information
Run this command and include output in bug reports:
```bash
python -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()}')
"
```

## What's Next?

After successful installation:
1. **Read the User Guide** for detailed feature explanations
2. **Try the examples** in the `examples/` directory
3. **Join the community** for tips and tricks
4. **Contribute** to the project on GitHub

Happy video editing! 🎬✨ 