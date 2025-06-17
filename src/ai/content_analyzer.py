"""
Content Analyzer for ClipForge
Uses GPT to analyze video content and suggest B-roll, meme moments, and enhancements
"""
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

from config import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class ContentSuggestion:
    """Data class for content suggestions"""
    timestamp: float
    duration: float
    suggestion_type: str  # 'broll', 'meme', 'zoom', 'emoji'
    description: str
    confidence: float
    details: Dict

@dataclass
class MemeDetection:
    """Data class for meme moment detection"""
    timestamp: float
    meme_type: str  # 'reaction', 'punchline', 'awkward', 'emphasis'
    text: str
    suggested_effects: List[str]
    confidence: float

class ContentAnalyzer:
    """
    Analyzes video content using GPT to suggest B-roll, meme moments, and enhancements
    """
    
    def __init__(self):
        """Initialize the content analyzer"""
        self.client = None
        if openai and config.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OpenAI not available - content analysis features disabled")
    
    def analyze_transcript_for_broll(self, transcript: str, video_duration: float) -> List[ContentSuggestion]:
        """
        Analyze transcript to suggest B-roll opportunities
        
        Args:
            transcript: Full transcript text
            video_duration: Duration of video in seconds
            
        Returns:
            List of B-roll suggestions
        """
        if not self.client:
            logger.warning("OpenAI client not available")
            return []
        
        try:
            prompt = self._create_broll_analysis_prompt(transcript, video_duration)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert video editor specializing in B-roll selection."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Parse response
            suggestions = self._parse_broll_suggestions(response.choices[0].message.content)
            logger.info(f"Generated {len(suggestions)} B-roll suggestions")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"B-roll analysis failed: {e}")
            return []
    
    def detect_meme_moments(self, captions: List[Dict]) -> List[MemeDetection]:
        """
        Detect moments suitable for meme effects
        
        Args:
            captions: List of caption dictionaries with start, end, text
            
        Returns:
            List of meme moment detections
        """
        if not self.client:
            return self._fallback_meme_detection(captions)
        
        try:
            # Prepare transcript segments for analysis
            segments = []
            for caption in captions:
                segments.append({
                    'timestamp': caption['start'],
                    'text': caption['text'],
                    'duration': caption['end'] - caption['start']
                })
            
            prompt = self._create_meme_detection_prompt(segments)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in viral video content and meme creation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1200
            )
            
            # Parse response
            meme_moments = self._parse_meme_detections(response.choices[0].message.content)
            logger.info(f"Detected {len(meme_moments)} meme moments")
            
            return meme_moments
            
        except Exception as e:
            logger.error(f"Meme detection failed: {e}")
            return self._fallback_meme_detection(captions)
    
    def suggest_video_enhancements(self, transcript: str, video_metadata: Dict) -> Dict[str, List[str]]:
        """
        Suggest overall video enhancements
        
        Args:
            transcript: Full video transcript
            video_metadata: Video properties (duration, fps, etc.)
            
        Returns:
            Dictionary of enhancement suggestions by category
        """
        if not self.client:
            return self._fallback_enhancement_suggestions()
        
        try:
            prompt = self._create_enhancement_prompt(transcript, video_metadata)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional video editor and content strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            enhancements = self._parse_enhancement_suggestions(response.choices[0].message.content)
            logger.info("Video enhancement suggestions generated")
            
            return enhancements
            
        except Exception as e:
            logger.error(f"Enhancement suggestion failed: {e}")
            return self._fallback_enhancement_suggestions()
    
    def _create_broll_analysis_prompt(self, transcript: str, duration: float) -> str:
        """Create prompt for B-roll analysis"""
        return f"""
        Analyze this video transcript and suggest B-roll opportunities:
        
        Transcript: "{transcript}"
        Video Duration: {duration} seconds
        
        For each B-roll suggestion, provide:
        1. Timestamp (in seconds from start)
        2. Duration (how long the B-roll should last)
        3. Description of what B-roll footage would enhance the content
        4. Confidence score (0.0-1.0)
        5. Category (product, location, concept, demonstration, etc.)
        
        Focus on moments where:
        - Concepts need visual explanation
        - Products or locations are mentioned
        - Technical demonstrations occur
        - Emotional moments could be enhanced
        
        Format your response as JSON array with this structure:
        [
            {{
                "timestamp": 15.5,
                "duration": 3.0,
                "description": "Show close-up of product features",
                "confidence": 0.8,
                "category": "product"
            }}
        ]
        
        Provide 3-7 suggestions maximum.
        """
    
    def _create_meme_detection_prompt(self, segments: List[Dict]) -> str:
        """Create prompt for meme moment detection"""
        segments_text = "\n".join([f"{seg['timestamp']:.1f}s: {seg['text']}" for seg in segments])
        
        return f"""
        Analyze these video segments for meme-worthy moments:
        
        {segments_text}
        
        Identify moments that would be enhanced by meme effects like:
        - Zoom effects for emphasis
        - Reaction emojis
        - Sound effects
        - Slow motion
        - Text overlays
        - Awkward pause emphasis
        
        For each meme moment, provide:
        1. Timestamp (exact time in seconds)
        2. Meme type (reaction, punchline, awkward, emphasis, surprise)
        3. Original text at that moment
        4. Suggested effects (zoom, emoji, sound, slowmo, text)
        5. Confidence score (0.0-1.0)
        
        Format as JSON array:
        [
            {{
                "timestamp": 42.3,
                "meme_type": "emphasis",
                "text": "wait, what?",
                "suggested_effects": ["zoom", "emoji_shocked", "sound_record_scratch"],
                "confidence": 0.9
            }}
        ]
        
        Focus on genuine moments that would be funny or engaging.
        """
    
    def _create_enhancement_prompt(self, transcript: str, metadata: Dict) -> str:
        """Create prompt for video enhancement suggestions"""
        return f"""
        Analyze this video content and suggest enhancements:
        
        Transcript: "{transcript}"
        Video Info: Duration {metadata.get('duration', 0):.1f}s, {metadata.get('fps', 0):.1f} fps
        
        Suggest improvements in these categories:
        1. Pacing (speed up/slow down sections)
        2. Audio (background music, sound effects)
        3. Visual (color grading, filters, transitions)
        4. Engagement (hooks, call-to-actions, interactive elements)
        5. Accessibility (caption styling, audio descriptions)
        
        Format as JSON object:
        {{
            "pacing": ["Speed up intro by 20%", "Add pause after key points"],
            "audio": ["Add upbeat background music", "Enhance voice clarity"],
            "visual": ["Increase contrast for better visibility"],
            "engagement": ["Add hook in first 3 seconds"],
            "accessibility": ["Use larger caption font", "Add audio descriptions"]
        }}
        
        Provide 2-4 actionable suggestions per category.
        """
    
    def _parse_broll_suggestions(self, response_text: str) -> List[ContentSuggestion]:
        """Parse GPT response for B-roll suggestions"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if not json_match:
                return []
            
            data = json.loads(json_match.group())
            suggestions = []
            
            for item in data:
                suggestion = ContentSuggestion(
                    timestamp=float(item.get('timestamp', 0)),
                    duration=float(item.get('duration', 3.0)),
                    suggestion_type='broll',
                    description=item.get('description', ''),
                    confidence=float(item.get('confidence', 0.5)),
                    details={'category': item.get('category', 'general')}
                )
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to parse B-roll suggestions: {e}")
            return []
    
    def _parse_meme_detections(self, response_text: str) -> List[MemeDetection]:
        """Parse GPT response for meme detections"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if not json_match:
                return []
            
            data = json.loads(json_match.group())
            detections = []
            
            for item in data:
                detection = MemeDetection(
                    timestamp=float(item.get('timestamp', 0)),
                    meme_type=item.get('meme_type', 'general'),
                    text=item.get('text', ''),
                    suggested_effects=item.get('suggested_effects', []),
                    confidence=float(item.get('confidence', 0.5))
                )
                detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Failed to parse meme detections: {e}")
            return []
    
    def _parse_enhancement_suggestions(self, response_text: str) -> Dict[str, List[str]]:
        """Parse GPT response for enhancement suggestions"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                return self._fallback_enhancement_suggestions()
            
            data = json.loads(json_match.group())
            return data
            
        except Exception as e:
            logger.error(f"Failed to parse enhancement suggestions: {e}")
            return self._fallback_enhancement_suggestions()
    
    def _fallback_meme_detection(self, captions: List[Dict]) -> List[MemeDetection]:
        """Fallback meme detection using keyword patterns"""
        keywords = {
            'reaction': ['wow', 'oh no', 'wait', 'what', 'seriously', 'really'],
            'emphasis': ['exactly', 'definitely', 'absolutely', 'totally', 'completely'],
            'awkward': ['um', 'uh', 'well', 'so', 'anyway'],
            'surprise': ['surprise', 'unexpected', 'sudden', 'shock', 'amazing']
        }
        
        detections = []
        
        for caption in captions:
            text = caption['text'].lower()
            for meme_type, words in keywords.items():
                for word in words:
                    if word in text:
                        detection = MemeDetection(
                            timestamp=caption['start'],
                            meme_type=meme_type,
                            text=caption['text'],
                            suggested_effects=['zoom', 'emoji'],
                            confidence=0.6
                        )
                        detections.append(detection)
                        break
        
        return detections
    
    def _fallback_enhancement_suggestions(self) -> Dict[str, List[str]]:
        """Fallback enhancement suggestions"""
        return {
            'pacing': ['Review pacing for slow sections', 'Add dynamic cuts'],
            'audio': ['Consider background music', 'Enhance audio clarity'],
            'visual': ['Improve lighting consistency', 'Add transitions'],
            'engagement': ['Add compelling intro', 'Include call-to-action'],
            'accessibility': ['Ensure readable captions', 'Consider audio descriptions']
        } 