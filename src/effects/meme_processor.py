"""
Meme Effects Processor for ClipForge
Handles zoom effects, emoji overlays, sound effects, and viral-style video modifications
"""
import os
import tempfile
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

try:
    import ffmpeg
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    logging.warning(f"Optional dependency not found: {e}")

from config import config
from src.utils.logger import setup_logger
from src.ai.content_analyzer import MemeDetection

logger = setup_logger(__name__)

class MemeEffectsProcessor:
    """
    Applies meme-style effects to videos including zooms, emojis, sound effects
    """
    
    def __init__(self):
        """Initialize meme effects processor"""
        self.emoji_library = self._load_emoji_library()
        self.sound_library = self._load_sound_library()
        self.temp_files = []
        
        logger.info("MemeEffectsProcessor initialized")
    
    def apply_meme_effects(self, video_path: str, meme_detections: List[MemeDetection]) -> str:
        """
        Apply meme effects to video based on detections
        
        Args:
            video_path: Path to input video
            meme_detections: List of detected meme moments
            
        Returns:
            str: Path to processed video with meme effects
        """
        if not meme_detections:
            logger.info("No meme effects to apply")
            return video_path
        
        try:
            # Create output path
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Apply effects sequentially
            current_video = video_path
            
            for detection in meme_detections:
                logger.info(f"Applying {detection.meme_type} effect at {detection.timestamp}s")
                
                if "zoom" in detection.suggested_effects:
                    current_video = self._apply_zoom_effect(current_video, detection)
                
                if any(effect.startswith("emoji") for effect in detection.suggested_effects):
                    emoji_type = next((e for e in detection.suggested_effects if e.startswith("emoji")), "emoji_fire")
                    current_video = self._apply_emoji_overlay(current_video, detection, emoji_type)
                
                if any(effect.startswith("sound") for effect in detection.suggested_effects):
                    sound_type = next((s for s in detection.suggested_effects if s.startswith("sound")), "sound_ding")
                    current_video = self._apply_sound_effect(current_video, detection, sound_type)
                
                if "slowmo" in detection.suggested_effects:
                    current_video = self._apply_slowmo_effect(current_video, detection)
                
                if "text" in detection.suggested_effects:
                    current_video = self._apply_text_overlay(current_video, detection)
            
            # Copy final result to output path
            if current_video != video_path:
                import shutil
                shutil.copy2(current_video, output_path)
            else:
                # No effects were applied
                shutil.copy2(video_path, output_path)
            
            logger.info(f"Meme effects applied successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to apply meme effects: {e}")
            return video_path
    
    def _apply_zoom_effect(self, video_path: str, detection: MemeDetection) -> str:
        """Apply zoom effect at specified timestamp"""
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Zoom parameters
            zoom_start = detection.timestamp
            zoom_duration = 0.5  # Half second zoom
            zoom_factor = 1.3    # 30% zoom
            
            # Create zoom filter
            zoom_filter = (
                f"[0:v]scale=iw*{zoom_factor}:ih*{zoom_factor},"
                f"crop=iw/{zoom_factor}:ih/{zoom_factor}:"
                f"(iw-ow)/2:(ih-oh)/2[zoomed];"
                f"[0:v][zoomed]overlay=enable='between(t,{zoom_start},{zoom_start + zoom_duration})'"
            )
            
            (
                ffmpeg
                .input(video_path)
                .filter_complex(zoom_filter)
                .output(output_path, vcodec='libx264', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Zoom effect failed: {e}")
            return video_path
    
    def _apply_emoji_overlay(self, video_path: str, detection: MemeDetection, emoji_type: str) -> str:
        """Apply emoji overlay effect"""
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Get emoji image
            emoji_path = self._get_emoji_path(emoji_type)
            if not emoji_path or not os.path.exists(emoji_path):
                logger.warning(f"Emoji not found: {emoji_type}")
                return video_path
            
            # Overlay parameters
            overlay_start = detection.timestamp
            overlay_duration = 1.0
            
            # Create overlay filter
            overlay_filter = (
                f"[1:v]scale=100:100[emoji];"
                f"[0:v][emoji]overlay=W-110:10:"
                f"enable='between(t,{overlay_start},{overlay_start + overlay_duration})'"
            )
            
            (
                ffmpeg
                .input(video_path)
                .input(emoji_path)
                .filter_complex(overlay_filter)
                .output(output_path, vcodec='libx264', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Emoji overlay failed: {e}")
            return video_path
    
    def _apply_sound_effect(self, video_path: str, detection: MemeDetection, sound_type: str) -> str:
        """Apply sound effect at timestamp"""
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Get sound file
            sound_path = self._get_sound_path(sound_type)
            if not sound_path or not os.path.exists(sound_path):
                logger.warning(f"Sound effect not found: {sound_type}")
                return video_path
            
            # Mix audio at specific timestamp
            audio_delay = detection.timestamp
            
            (
                ffmpeg
                .input(video_path)
                .input(sound_path)
                .filter_complex(f"[1:a]adelay={int(audio_delay * 1000)}|{int(audio_delay * 1000)}[delayed]; [0:a][delayed]amix=inputs=2")
                .output(output_path, vcodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Sound effect failed: {e}")
            return video_path
    
    def _apply_slowmo_effect(self, video_path: str, detection: MemeDetection) -> str:
        """Apply slow motion effect"""
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Slow motion parameters
            slowmo_start = detection.timestamp
            slowmo_duration = 2.0
            slowmo_factor = 0.5  # Half speed
            
            # Create slowmo filter
            slowmo_filter = (
                f"setpts=if(between(t,{slowmo_start},{slowmo_start + slowmo_duration}),"
                f"PTS/{slowmo_factor},PTS)"
            )
            
            (
                ffmpeg
                .input(video_path)
                .filter('video', slowmo_filter)
                .output(output_path, vcodec='libx264', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Slow motion effect failed: {e}")
            return video_path
    
    def _apply_text_overlay(self, video_path: str, detection: MemeDetection) -> str:
        """Apply text overlay effect"""
        try:
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            self.temp_files.append(output_path)
            
            # Text overlay parameters
            text = self._generate_meme_text(detection)
            overlay_start = detection.timestamp
            overlay_duration = 1.5
            
            # Create text overlay filter
            text_filter = (
                f"drawtext=text='{text}':"
                f"x=(w-text_w)/2:y=h-100:"
                f"fontsize=36:fontcolor=white:bordercolor=black:borderw=2:"
                f"enable='between(t,{overlay_start},{overlay_start + overlay_duration})'"
            )
            
            (
                ffmpeg
                .input(video_path)
                .filter('video', text_filter)
                .output(output_path, vcodec='libx264', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Text overlay failed: {e}")
            return video_path
    
    def _generate_meme_text(self, detection: MemeDetection) -> str:
        """Generate meme text based on detection"""
        meme_texts = {
            'reaction': ['BRUH', 'WAIT WHAT?', 'NO WAY', 'OMG'],
            'emphasis': ['EXACTLY!', 'THIS!', 'FACTS', 'TRUTH'],
            'awkward': ['...', 'AWKWARD', 'UH OH', 'YIKES'],
            'surprise': ['PLOT TWIST', 'SURPRISE!', 'WHOA', 'UNEXPECTED']
        }
        
        texts = meme_texts.get(detection.meme_type, ['WOW'])
        # Simple selection based on text content
        if 'wait' in detection.text.lower():
            return 'WAIT WHAT?'
        elif 'oh' in detection.text.lower():
            return 'OH NO'
        else:
            return texts[0]
    
    def _load_emoji_library(self) -> Dict[str, str]:
        """Load emoji library paths"""
        # In a real implementation, this would load actual emoji files
        emoji_library = {
            'emoji_fire': 'assets/emojis/fire.png',
            'emoji_shocked': 'assets/emojis/shocked.png',
            'emoji_laughing': 'assets/emojis/laughing.png',
            'emoji_thinking': 'assets/emojis/thinking.png',
            'emoji_clap': 'assets/emojis/clap.png'
        }
        
        # Create placeholder emoji files if they don't exist
        self._create_placeholder_emojis(emoji_library)
        
        return emoji_library
    
    def _load_sound_library(self) -> Dict[str, str]:
        """Load sound effects library"""
        return {
            'sound_ding': 'assets/sounds/ding.wav',
            'sound_record_scratch': 'assets/sounds/record_scratch.wav',
            'sound_airhorn': 'assets/sounds/airhorn.wav',
            'sound_whoosh': 'assets/sounds/whoosh.wav',
            'sound_pop': 'assets/sounds/pop.wav'
        }
    
    def _get_emoji_path(self, emoji_type: str) -> Optional[str]:
        """Get path to emoji file"""
        return self.emoji_library.get(emoji_type)
    
    def _get_sound_path(self, sound_type: str) -> Optional[str]:
        """Get path to sound file"""
        return self.sound_library.get(sound_type)
    
    def _create_placeholder_emojis(self, emoji_library: Dict[str, str]):
        """Create placeholder emoji images if they don't exist"""
        os.makedirs("assets/emojis", exist_ok=True)
        
        for emoji_type, path in emoji_library.items():
            if not os.path.exists(path):
                try:
                    # Create a simple colored circle as placeholder
                    img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
                    draw = ImageDraw.Draw(img)
                    
                    # Different colors for different emojis
                    colors = {
                        'emoji_fire': (255, 100, 0, 255),
                        'emoji_shocked': (255, 255, 0, 255),
                        'emoji_laughing': (0, 255, 0, 255),
                        'emoji_thinking': (0, 100, 255, 255),
                        'emoji_clap': (255, 0, 255, 255)
                    }
                    
                    color = colors.get(emoji_type, (128, 128, 128, 255))
                    draw.ellipse([10, 10, 90, 90], fill=color)
                    
                    # Add simple emoji symbol
                    try:
                        font = ImageFont.load_default()
                        symbols = {
                            'emoji_fire': '🔥',
                            'emoji_shocked': '😱', 
                            'emoji_laughing': '😂',
                            'emoji_thinking': '🤔',
                            'emoji_clap': '👏'
                        }
                        symbol = symbols.get(emoji_type, '😊')
                        
                        # Get text size and center it
                        bbox = draw.textbbox((0, 0), symbol, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        x = (100 - text_width) // 2
                        y = (100 - text_height) // 2
                        
                        draw.text((x, y), symbol, fill=(255, 255, 255, 255), font=font)
                        
                    except Exception:
                        # Fallback to simple text
                        draw.text((35, 40), emoji_type[-1].upper(), fill=(255, 255, 255, 255))
                    
                    img.save(path, 'PNG')
                    logger.info(f"Created placeholder emoji: {path}")
                    
                except Exception as e:
                    logger.error(f"Failed to create placeholder emoji {emoji_type}: {e}")
    
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