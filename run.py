#!/usr/bin/env python3
"""
ClipForge Application Launcher
Simple script to run the Streamlit application
"""
import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'opencv-python',
        'ffmpeg-python',
        'openai-whisper',
        'openai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is installed and accessible")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg not found. Please install FFmpeg:")
    print("   - Windows: Download from https://ffmpeg.org/download.html")
    print("   - macOS: brew install ffmpeg")
    print("   - Linux: sudo apt install ffmpeg")
    return False

def main():
    """Main application launcher"""
    print("🎬 ClipForge - AI Video Editor")
    print("=" * 40)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("⚠️  FFmpeg not found - some features may not work")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check for API keys
    print("🔑 Checking API configuration...")
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  No .env file found. Create one with your API keys:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print("   See .env.example for full configuration")
    
    # Launch Streamlit
    print("🚀 Starting ClipForge...")
    print("📱 App will open in your browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    
    try:
        subprocess.run(['streamlit', 'run', 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 ClipForge stopped. Thanks for using ClipForge!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Install it with:")
        print("   pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main() 