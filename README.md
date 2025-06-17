# ClipForge 🎬✨

An AI-powered video editor that automatically generates captions, adds B-roll footage, and creates viral-ready content with "Meme Mode" effects.

## Features

### 🎯 Current (MVP)
- [x] Project initialization
- [ ] Audio extraction with FFmpeg
- [ ] Automatic transcription with Whisper
- [ ] Caption generation and overlay
- [ ] Video export functionality

### 🚀 Planned (v2+)
- [ ] B-roll suggestion and insertion (GPT-powered)
- [ ] Meme Mode: emojis, zooms, sound effects
- [ ] Drag-and-drop interface
- [ ] Custom caption styles/themes
- [ ] Cloud sync with Supabase
- [ ] Batch processing for creators

## Architecture

- **Frontend**: Streamlit for web interface with drag-and-drop
- **Backend**: Python with FFmpeg for video processing
- **AI Models**: OpenAI Whisper (transcription) + GPT (content analysis)
- **Storage**: Local SQLite + optional Supabase integration
- **Processing**: FFmpeg pipeline for video editing

## Quick Start

```bash
# Clone the repository
git clone https://github.com/noahwilliamshaffer/AiVideoEditor.git
cd AiVideoEditor

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key (required for AI features)
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run the application
python run.py
```

The app will automatically open in your browser at `http://localhost:8501`

For detailed installation instructions, see [INSTALL.md](INSTALL.md)

## Development Roadmap

### Phase 1: Core Foundation ✅
- [x] Project structure
- [x] FFmpeg integration
- [x] Whisper transcription
- [x] Basic caption overlay

### Phase 2: AI Enhancement ✅
- [x] GPT content analysis
- [x] B-roll recommendation engine
- [x] Intelligent scene detection

### Phase 3: Meme Mode ✅
- [x] Emoji overlay system
- [x] Zoom effects
- [x] Sound effect integration
- [x] Viral content templates

### Phase 4: Polish & Scale
- [ ] Advanced UI/UX
- [ ] Cloud synchronization
- [ ] Batch processing
- [ ] Custom themes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make atomic commits with semantic prefixes
4. Submit a pull request

## License

MIT License - see LICENSE file for details 