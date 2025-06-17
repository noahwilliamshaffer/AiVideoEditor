"""
UI Components for ClipForge Streamlit Interface
"""
import streamlit as st
import cv2
import numpy as np
from pathlib import Path
from config import config

def create_sidebar():
    """Create and populate the sidebar with app info and settings"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/FF6B6B/FFFFFF?text=ClipForge", width=200)
        
        st.markdown("### 🎬 ClipForge")
        st.markdown("*AI-Powered Video Editor*")
        
        st.markdown("---")
        
        # App statistics
        st.markdown("### 📊 Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Videos Processed", "0", "0")
        with col2:
            st.metric("Total Time Saved", "0m", "0m")
        
        st.markdown("---")
        
        # Quick settings
        st.markdown("### ⚙️ Quick Settings")
        
        # Theme selector
        theme = st.selectbox(
            "UI Theme",
            ["Auto", "Light", "Dark"],
            help="Choose your preferred UI theme"
        )
        
        # Processing priority
        priority = st.selectbox(
            "Processing Priority",
            ["Speed", "Balanced", "Quality"],
            index=1,
            help="Speed: Faster processing, lower quality\nQuality: Slower processing, higher quality"
        )
        
        st.markdown("---")
        
        # Help and about
        with st.expander("ℹ️ About ClipForge"):
            st.markdown("""
            **ClipForge** transforms your videos with AI-powered features:
            
            - 🎤 **Auto Captions**: Whisper-powered transcription
            - 😄 **Meme Mode**: Viral effects and overlays  
            - 🎥 **B-roll**: AI-suggested content insertion
            - 🎨 **Custom Styles**: Multiple caption themes
            
            Built with ❤️ using Streamlit, OpenAI, and FFmpeg
            """)
        
        with st.expander("🆘 Help & Support"):
            st.markdown("""
            **Need help?**
            
            - 📖 Check the [Documentation](https://github.com/noahwilliamshaffer/AiVideoEditor)
            - 🐛 Report issues on [GitHub](https://github.com/noahwilliamshaffer/AiVideoEditor/issues)
            - 💬 Join our community Discord
            
            **System Requirements:**
            - FFmpeg installed and accessible
            - OpenAI API key (for GPT features)
            - 4GB+ RAM recommended
            """)

def display_video_info(uploaded_file):
    """Display information about the uploaded video file"""
    if uploaded_file is None:
        return
    
    # File info
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("File Size", f"{file_size_mb:.1f} MB")
    
    with col2:
        st.metric("Format", uploaded_file.type.split('/')[-1].upper())
    
    with col3:
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            st.error(f"⚠️ File too large (>{config.MAX_FILE_SIZE_MB}MB)")
        else:
            st.success("✅ Valid file")
    
    # Video preview (if possible)
    try:
        # Create a temporary file to read video properties
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Get video properties using OpenCV
        cap = cv2.VideoCapture(tmp_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Display video properties
            st.markdown("### 📹 Video Properties")
            
            prop_col1, prop_col2, prop_col3, prop_col4 = st.columns(4)
            
            with prop_col1:
                st.metric("Duration", f"{duration:.1f}s")
            
            with prop_col2:
                st.metric("Resolution", f"{width}x{height}")
            
            with prop_col3:
                st.metric("FPS", f"{fps:.1f}")
            
            with prop_col4:
                st.metric("Frames", f"{frame_count:,}")
            
            cap.release()
        
        # Clean up temp file
        import os
        os.unlink(tmp_path)
        
    except Exception as e:
        st.warning(f"Could not read video properties: {e}")
    
    # Display video player
    st.markdown("### 🎬 Preview")
    st.video(uploaded_file)

def display_processing_progress(status: str, progress: float = 0.0, message: str = ""):
    """Display processing progress with status and progress bar"""
    
    status_colors = {
        "ready": "🟢",
        "processing": "🟡", 
        "completed": "✅",
        "error": "❌",
        "warning": "⚠️"
    }
    
    status_icon = status_colors.get(status, "⚪")
    
    # Status header
    st.markdown(f"### {status_icon} {status.title()}")
    
    if message:
        st.text(message)
    
    # Progress bar for processing
    if status == "processing" and progress > 0:
        st.progress(progress)
        st.text(f"Progress: {progress*100:.1f}%")

def create_results_display(output_path: str, processing_time: float, original_file_name: str):
    """Display processing results and download options"""
    
    st.success("🎉 Video processing completed!")
    
    # Processing summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Processing Time", f"{processing_time:.1f}s")
    
    with col2:
        # Calculate file size
        import os
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            st.metric("Output Size", f"{size_mb:.1f} MB")
    
    with col3:
        st.metric("Status", "✅ Complete")
    
    # Download section
    st.markdown("### 📥 Download Results")
    
    if os.path.exists(output_path):
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Download Processed Video",
                data=file.read(),
                file_name=f"clipforge_{original_file_name}",
                mime="video/mp4",
                type="primary",
                use_container_width=True
            )
        
        # Preview processed video
        st.markdown("### 🎬 Processed Video Preview")
        st.video(output_path)
        
    else:
        st.error("Output file not found. Please try processing again.")

def display_feature_card(title: str, description: str, icon: str, available: bool = True):
    """Display a feature card with title, description and availability status"""
    
    status = "✅ Available" if available else "🚧 Coming Soon"
    status_color = "green" if available else "orange"
    
    with st.container():
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd; 
                border-radius: 10px; 
                padding: 15px; 
                margin: 10px 0;
                background-color: {'#f0f9ff' if available else '#fef3c7'};
            ">
                <h4>{icon} {title}</h4>
                <p>{description}</p>
                <span style="color: {status_color}; font-weight: bold;">{status}</span>
            </div>
            """,
            unsafe_allow_html=True
        ) 