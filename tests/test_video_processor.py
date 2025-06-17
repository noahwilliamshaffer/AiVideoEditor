"""
Unit tests for VideoProcessor class
"""
import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.append('..')

from src.video_processor import VideoProcessor

class TestVideoProcessor(unittest.TestCase):
    """Test cases for VideoProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = VideoProcessor()
        
        # Create a temporary video file path for testing
        self.temp_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        self.temp_video.close()
        
    def tearDown(self):
        """Clean up after tests"""
        # Clean up temporary files
        if os.path.exists(self.temp_video.name):
            os.unlink(self.temp_video.name)
        
        # Clean up processor temp files
        self.processor.cleanup()
    
    def test_processor_initialization(self):
        """Test processor initializes correctly"""
        self.assertIsNone(self.processor.video_path)
        self.assertIsNone(self.processor.audio_path)
        self.assertIsNone(self.processor.transcript)
        self.assertEqual(self.processor.captions, [])
        self.assertEqual(self.processor.temp_files, [])
    
    @patch('cv2.VideoCapture')
    def test_load_video_success(self, mock_cv2):
        """Test successful video loading"""
        # Mock OpenCV VideoCapture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = [30.0, 900, 1920, 1080]  # fps, frame_count, width, height
        mock_cv2.return_value = mock_cap
        
        # Create a dummy video file
        with open(self.temp_video.name, 'wb') as f:
            f.write(b'dummy video content')
        
        result = self.processor.load_video(self.temp_video.name)
        
        self.assertTrue(result)
        self.assertEqual(self.processor.video_path, self.temp_video.name)
        self.assertEqual(self.processor.fps, 30.0)
        self.assertEqual(self.processor.width, 1920)
        self.assertEqual(self.processor.height, 1080)
        self.assertEqual(self.processor.duration, 30.0)  # 900 frames / 30 fps
    
    def test_load_video_file_not_found(self):
        """Test loading non-existent video file"""
        result = self.processor.load_video("nonexistent.mp4")
        self.assertFalse(result)
    
    @patch('ffmpeg.input')
    @patch('ffmpeg.output')
    def test_extract_audio(self, mock_output, mock_input):
        """Test audio extraction"""
        # Set up processor with video
        self.processor.video_path = self.temp_video.name
        
        # Mock ffmpeg chain
        mock_chain = Mock()
        mock_input.return_value = mock_chain
        mock_chain.output.return_value = mock_chain
        mock_chain.overwrite_output.return_value = mock_chain
        mock_chain.run.return_value = None
        
        audio_path = self.processor.extract_audio()
        
        self.assertIsNotNone(audio_path)
        self.assertTrue(audio_path.endswith('.wav'))
        self.assertIn(audio_path, self.processor.temp_files)
    
    def test_extract_audio_no_video(self):
        """Test audio extraction without loaded video"""
        with self.assertRaises(ValueError):
            self.processor.extract_audio()
    
    @patch('whisper.load_model')
    def test_transcribe_audio(self, mock_whisper):
        """Test audio transcription"""
        # Set up audio path
        self.processor.audio_path = "/fake/audio.wav"
        
        # Mock Whisper model and result
        mock_model = Mock()
        mock_result = {
            "text": "Hello world",
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Hello world",
                    "avg_logprob": -0.5
                }
            ]
        }
        mock_model.transcribe.return_value = mock_result
        mock_whisper.return_value = mock_model
        
        result = self.processor.transcribe_audio("base")
        
        self.assertEqual(result, mock_result)
        self.assertEqual(len(self.processor.captions), 1)
        self.assertEqual(self.processor.captions[0]["text"], "Hello world")
        self.assertEqual(self.processor.captions[0]["start"], 0.0)
        self.assertEqual(self.processor.captions[0]["end"], 2.0)
    
    def test_transcribe_audio_no_audio(self):
        """Test transcription without audio file"""
        with self.assertRaises(ValueError):
            self.processor.transcribe_audio()
    
    def test_seconds_to_srt_time(self):
        """Test SRT time conversion"""
        # Test various time conversions
        self.assertEqual(self.processor._seconds_to_srt_time(0.0), "00:00:00,000")
        self.assertEqual(self.processor._seconds_to_srt_time(1.5), "00:00:01,500")
        self.assertEqual(self.processor._seconds_to_srt_time(65.25), "00:01:05,250")
        self.assertEqual(self.processor._seconds_to_srt_time(3661.75), "01:01:01,750")
    
    def test_get_caption_filter(self):
        """Test caption filter generation"""
        standard_filter = self.processor._get_caption_filter("Standard")
        self.assertIn("force_style", standard_filter)
        
        tiktok_filter = self.processor._get_caption_filter("TikTok")
        self.assertIn("Bold=1", tiktok_filter["force_style"])
        
        youtube_filter = self.processor._get_caption_filter("YouTube")
        self.assertIn("FontSize=28", youtube_filter["force_style"])
    
    def test_cleanup(self):
        """Test temporary file cleanup"""
        # Create some fake temp files
        temp_files = []
        for i in range(3):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.close()
            temp_files.append(temp_file.name)
            self.processor.temp_files.append(temp_file.name)
        
        # Verify files exist
        for temp_file in temp_files:
            self.assertTrue(os.path.exists(temp_file))
        
        # Cleanup
        self.processor.cleanup()
        
        # Verify files are deleted
        for temp_file in temp_files:
            self.assertFalse(os.path.exists(temp_file))
        
        # Verify temp_files list is cleared
        self.assertEqual(len(self.processor.temp_files), 0)

if __name__ == '__main__':
    unittest.main() 