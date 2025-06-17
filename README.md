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

## Installation

```bash
# Clone the repository
git clone https://github.com/noahwilliamshaffer/AiVideoEditor.git
cd AiVideoEditor

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Development Roadmap

### Phase 1: Core Foundation ✅
- [x] Project structure
- [ ] FFmpeg integration
- [ ] Whisper transcription
- [ ] Basic caption overlay

### Phase 2: AI Enhancement
- [ ] GPT content analysis
- [ ] B-roll recommendation engine
- [ ] Intelligent scene detection

### Phase 3: Meme Mode
- [ ] Emoji overlay system
- [ ] Zoom effects
- [ ] Sound effect integration
- [ ] Viral content templates

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