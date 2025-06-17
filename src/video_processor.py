"""
VideoProcessor - Core video processing functionality for ClipForge
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging

# Third-party imports with error handling
try:
    import whisper
    import openai
    import ffmpeg
    import cv2
    import numpy as np
except ImportError as e:
    logging.warning(f"Optional dependency not found: {e}")

from config import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class VideoProcessor:
    """
    Main video processing class for ClipForge
    Handles transcription, caption generation, and video effects
    """
    
    def __init__(self):
        """Initialize the video processor"""
        self.video_path: Optional[str] = None
        self.audio_path: Optional[str] = None
        self.transcript: Optional[Dict] = None
        self.captions: List[Dict] = []
        self.output_path: Optional[str] = None
        self.temp_files: List[str] = []
        
        # Video properties
        self.duration: float = 0.0
        self.fps: float = 0.0
        self.width: int = 0
        self.height: int = 0
        
        logger.info("VideoProcessor initialized")
    
    def load_video(self, video_path: str) -> bool:
        """
        Load video file and extract basic properties
        
        Args:
            video_path: Path to the input video file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            self.video_path = video_path
            
            # Get video properties using OpenCV
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.duration = frame_count / self.fps if self.fps > 0 else 0
            
            cap.release()
            
            logger.info(f"Video loaded: {video_path}")
            logger.info(f"Properties: {self.width}x{self.height}, {self.fps:.2f}fps, {self.duration:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load video: {e}")
            return False
    
    def extract_audio(self) -> str:
        """
        Extract audio from video file
        
        Returns:
            str: Path to extracted audio file
        """
        if not self.video_path:
            raise ValueError("No video loaded")
        
        try:
            # Create temp audio file
            audio_fd, self.audio_path = tempfile.mkstemp(suffix=".wav")
            os.close(audio_fd)
            self.temp_files.append(self.audio_path)
            
            # Extract audio using ffmpeg
            (
                ffmpeg
                .input(self.video_path)
                .output(self.audio_path, acodec='pcm_s16le', ac=1, ar='16000')
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"Audio extracted to: {self.audio_path}")
            return self.audio_path
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            raise
    
    def transcribe_audio(self, model: str = "base") -> Dict:
        """
        Transcribe audio using Whisper
        
        Args:
            model: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            
        Returns:
            Dict: Transcription result with segments and text
        """
        if not self.audio_path:
            raise ValueError("No audio file available. Run extract_audio() first.")
        
        try:
            logger.info(f"Starting transcription with {model} model...")
            
            # Load Whisper model
            whisper_model = whisper.load_model(model, device=config.WHISPER_DEVICE)
            
            # Transcribe
            result = whisper_model.transcribe(
                self.audio_path,
                language="en",  # Auto-detect or specify language
                task="transcribe"
            )
            
            self.transcript = result
            
            # Convert to caption format
            self.captions = []
            for segment in result["segments"]:
                self.captions.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "confidence": segment.get("avg_logprob", 0.0)
                })
            
            logger.info(f"Transcription completed: {len(self.captions)} captions generated")
            return self.transcript
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def add_captions(self, style: str = "Standard") -> str:
        """
        Add captions to video
        
        Args:
            style: Caption style ('Standard', 'TikTok', 'YouTube', 'Custom')
            
        Returns:
            str: Path to video with captions
        """
        if not self.captions:
            raise ValueError("No captions available. Run transcribe_audio() first.")
        
        try:
            # Create subtitle file
            srt_fd, srt_path = tempfile.mkstemp(suffix=".srt")
            self.temp_files.append(srt_path)
            
            with os.fdopen(srt_fd, 'w', encoding='utf-8') as f:
                for i, caption in enumerate(self.captions, 1):
                    start_time = self._seconds_to_srt_time(caption["start"])
                    end_time = self._seconds_to_srt_time(caption["end"])
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{caption['text']}\n\n")
            
            # Create output path
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Get caption styling based on style parameter
            caption_filter = self._get_caption_filter(style)
            
            # Add captions using ffmpeg
            (
                ffmpeg
                .input(self.video_path)
                .filter('subtitles', srt_path, **caption_filter)
                .output(output_path, vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(quiet=True)
            )
            
            self.output_path = output_path
            logger.info(f"Captions added with {style} style")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Caption addition failed: {e}")
            raise
    
    def apply_meme_effects(self) -> str:
        """
        Apply meme-style effects to video
        
        Returns:
            str: Path to video with meme effects
        """
        if not self.output_path and not self.video_path:
            raise ValueError("No video available for meme effects")
        
        input_path = self.output_path or self.video_path
        
        try:
            # Create output path
            meme_fd, meme_output = tempfile.mkstemp(suffix=".mp4")
            os.close(meme_fd)
            self.temp_files.append(meme_output)
            
            # Apply meme effects (zoom, shake, etc.)
            # This is a simplified version - full implementation would be more complex
            zoom_filter = "scale=iw*1.1:ih*1.1,crop=iw/1.1:ih/1.1"
            
            (
                ffmpeg
                .input(input_path)
                .filter_complex(
                    f"[0:v]{zoom_filter}[zoomed];"
                    "[zoomed]fps=30[output]"
                )
                .output(meme_output, map="[output]", map="0:a", vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(quiet=True)
            )
            
            self.output_path = meme_output
            logger.info("Meme effects applied")
            
            return meme_output
            
        except Exception as e:
            logger.error(f"Meme effects application failed: {e}")
            raise
    
    def export_video(self, output_dir: str = None) -> str:
        """
        Export the final processed video
        
        Args:
            output_dir: Output directory (uses config.OUTPUT_DIR if None)
            
        Returns:
            str: Path to exported video file
        """
        if not self.output_path:
            raise ValueError("No processed video available")
        
        try:
            output_dir = output_dir or config.OUTPUT_DIR
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time())
            final_output = os.path.join(output_dir, f"clipforge_output_{timestamp}.mp4")
            
            # Copy to final location
            import shutil
            shutil.copy2(self.output_path, final_output)
            
            logger.info(f"Video exported to: {final_output}")
            return final_output
            
        except Exception as e:
            logger.error(f"Video export failed: {e}")
            raise
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_file}: {e}")
        
        self.temp_files.clear()
        logger.info("Temporary files cleaned up")
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _get_caption_filter(self, style: str) -> Dict:
        """Get FFmpeg caption filter parameters based on style"""
        styles = {
            "Standard": {
                "force_style": f"FontSize={config.CAPTION_FONT_SIZE},PrimaryColour=&H{config.CAPTION_FONT_COLOR.replace('#', '')}"
            },
            "TikTok": {
                "force_style": "FontSize=32,Bold=1,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2"
            },
            "YouTube": {
                "force_style": "FontSize=28,PrimaryColour=&HFFFFFF,BackColour=&H80000000"
            },
            "Custom": {
                "force_style": f"FontSize={config.CAPTION_FONT_SIZE},PrimaryColour=&H{config.CAPTION_FONT_COLOR.replace('#', '')}"
            }
        }
        
        return styles.get(style, styles["Standard"])
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup() 