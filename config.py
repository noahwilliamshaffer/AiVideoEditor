"""
Configuration settings for ClipForge AI Video Editor
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Supabase (Optional)
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
    
    # FFmpeg Configuration
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    
    # Whisper Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")
    
    # Caption Settings
    CAPTION_FONT_SIZE: int = int(os.getenv("CAPTION_FONT_SIZE", "24"))
    CAPTION_FONT_COLOR: str = os.getenv("CAPTION_FONT_COLOR", "white")
    CAPTION_BACKGROUND_COLOR: str = os.getenv("CAPTION_BACKGROUND_COLOR", "black")
    CAPTION_POSITION: str = os.getenv("CAPTION_POSITION", "bottom")
    
    # Directories
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs("cache", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

# Initialize configuration
config = Config()
config.ensure_directories() 