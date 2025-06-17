"""
Simplified Meme Effects for ClipForge
Basic zoom, overlay, and enhancement effects for viral video content
"""
import os
import tempfile
from typing import List, Dict, Optional
import logging

try:
    import ffmpeg
except ImportError:
    ffmpeg = None

from config import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class SimpleMemeEffects:
    """
    Simple meme effects processor for viral video enhancements
    """
    
    def __init__(self):
        """Initialize meme effects processor"""
        self.temp_files = []
        logger.info("SimpleMemeEffects initialized")
    
    def apply_zoom_effect(self, video_path: str, timestamp: float, duration: float = 0.5) -> str:
        """
        Apply zoom effect at specified timestamp
        
        Args:
            video_path: Input video path
            timestamp: When to start zoom effect
            duration: How long the zoom lasts
            
        Returns:
            str: Path to video with zoom effect
        """
        if not ffmpeg:
            logger.warning("FFmpeg not available for zoom effect")
            return video_path
        
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Simple zoom effect using scale filter
            zoom_factor = 1.2
            
            (
                ffmpeg
                .input(video_path)
                .filter('scale', f'iw*{zoom_factor}', f'ih*{zoom_factor}')
                .filter('crop', f'iw/{zoom_factor}', f'ih/{zoom_factor}', '(iw-ow)/2', '(ih-oh)/2')
                .output(output_path, vcodec='libx264', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"Zoom effect applied at {timestamp}s")
            return output_path
            
        except Exception as e:
            logger.error(f"Zoom effect failed: {e}")
            return video_path
    
    def apply_speed_effect(self, video_path: str, speed_factor: float = 1.5) -> str:
        """
        Apply speed up effect to entire video
        
        Args:
            video_path: Input video path
            speed_factor: Speed multiplier (1.5 = 50% faster)
            
        Returns:
            str: Path to sped up video
        """
        if not ffmpeg:
            logger.warning("FFmpeg not available for speed effect")
            return video_path
        
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            (
                ffmpeg
                .input(video_path)
                .filter('setpts', f'PTS/{speed_factor}')
                .filter('atempo', speed_factor)
                .output(output_path, vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"Speed effect applied: {speed_factor}x")
            return output_path
            
        except Exception as e:
            logger.error(f"Speed effect failed: {e}")
            return video_path
    
    def add_text_overlay(self, video_path: str, text: str, timestamp: float, duration: float = 2.0) -> str:
        """
        Add text overlay to video
        
        Args:
            video_path: Input video path
            text: Text to overlay
            timestamp: When to show text
            duration: How long to show text
            
        Returns:
            str: Path to video with text overlay
        """
        if not ffmpeg:
            logger.warning("FFmpeg not available for text overlay")
            return video_path
        
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Clean text for FFmpeg
            clean_text = text.replace("'", "").replace('"', '').replace(':', '\\:')
            
            (
                ffmpeg
                .input(video_path)
                .filter('drawtext', 
                       text=clean_text,
                       x='(w-text_w)/2',
                       y='h-100',
                       fontsize=48,
                       fontcolor='white',
                       bordercolor='black',
                       borderw=3,
                       enable=f'between(t,{timestamp},{timestamp + duration})')
                .output(output_path, vcodec='libx264', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"Text overlay added: '{text}' at {timestamp}s")
            return output_path
            
        except Exception as e:
            logger.error(f"Text overlay failed: {e}")
            return video_path
    
    def enhance_colors(self, video_path: str, saturation: float = 1.3, brightness: float = 1.1) -> str:
        """
        Enhance video colors for more vibrant look
        
        Args:
            video_path: Input video path
            saturation: Saturation multiplier
            brightness: Brightness multiplier
            
        Returns:
            str: Path to color-enhanced video
        """
        if not ffmpeg:
            logger.warning("FFmpeg not available for color enhancement")
            return video_path
        
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            (
                ffmpeg
                .input(video_path)
                .filter('eq', saturation=saturation, brightness=brightness-1)
                .output(output_path, vcodec='libx264', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"Color enhancement applied: sat={saturation}, bright={brightness}")
            return output_path
            
        except Exception as e:
            logger.error(f"Color enhancement failed: {e}")
            return video_path
    
    def create_meme_compilation(self, video_paths: List[str]) -> str:
        """
        Create a compilation of multiple videos (basic concatenation)
        
        Args:
            video_paths: List of video file paths
            
        Returns:
            str: Path to compiled video
        """
        if not ffmpeg or len(video_paths) < 2:
            logger.warning("Cannot create compilation: insufficient videos or FFmpeg unavailable")
            return video_paths[0] if video_paths else ""
        
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Create input streams
            inputs = [ffmpeg.input(path) for path in video_paths]
            
            # Concatenate videos
            (
                ffmpeg
                .concat(*inputs, v=1, a=1)
                .output(output_path, vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"Meme compilation created from {len(video_paths)} videos")
            return output_path
            
        except Exception as e:
            logger.error(f"Compilation creation failed: {e}")
            return video_paths[0] if video_paths else ""
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_file}: {e}")
        
        self.temp_files.clear()
        logger.info("Meme effects temporary files cleaned up")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup() 