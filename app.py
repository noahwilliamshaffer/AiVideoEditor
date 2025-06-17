"""
ClipForge - AI Video Editor
Main Streamlit Application
"""
import streamlit as st
import os
import tempfile
from pathlib import Path
import logging
from config import config
from src.video_processor import VideoProcessor
from src.ui.components import create_sidebar, display_video_info
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger()

# Page configuration
st.set_page_config(
    page_title="ClipForge - AI Video Editor",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    st.title("🎬 ClipForge - AI Video Editor")
    st.markdown("*Transform your videos with AI-powered captions, B-roll, and meme effects*")
    
    # Initialize session state
    if 'processor' not in st.session_state:
        st.session_state.processor = VideoProcessor()
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = "ready"
    
    # Sidebar
    create_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📤 Upload Video")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            help=f"Maximum file size: {config.MAX_FILE_SIZE_MB}MB"
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            
            # Display video info
            display_video_info(uploaded_file)
            
            # Processing options
            st.subheader("🎛️ Processing Options")
            
            col_auto_caption, col_meme_mode, col_broll = st.columns(3)
            
            with col_auto_caption:
                auto_caption = st.checkbox("🎬 Auto Captions", value=True, help="Generate automatic captions using Whisper")
            
            with col_meme_mode:
                meme_mode = st.checkbox("😄 Meme Mode", help="Add emojis, zooms, and viral effects")
            
            with col_broll:
                add_broll = st.checkbox("🎥 Add B-roll", help="AI-suggested B-roll insertion (Coming Soon)")
            
            # Advanced settings
            with st.expander("⚙️ Advanced Settings"):
                whisper_model = st.selectbox(
                    "Whisper Model",
                    ["tiny", "base", "small", "medium", "large"],
                    index=1,
                    help="Larger models are more accurate but slower"
                )
                
                caption_style = st.selectbox(
                    "Caption Style",
                    ["Standard", "TikTok", "YouTube", "Custom"],
                    help="Pre-defined caption styles"
                )
                
                if caption_style == "Custom":
                    font_size = st.slider("Font Size", 16, 48, config.CAPTION_FONT_SIZE)
                    font_color = st.color_picker("Font Color", "#FFFFFF")
                    bg_color = st.color_picker("Background Color", "#000000")
            
            # Process button
            if st.button("🚀 Process Video", type="primary", use_container_width=True):
                if st.session_state.processing_status != "processing":
                    process_video(
                        uploaded_file,
                        auto_caption,
                        meme_mode,
                        add_broll,
                        whisper_model,
                        caption_style
                    )
    
    with col2:
        st.header("📊 Status")
        
        # Processing status
        status_placeholder = st.empty()
        
        if st.session_state.processing_status == "ready":
            status_placeholder.info("🟢 Ready to process video")
        elif st.session_state.processing_status == "processing":
            status_placeholder.warning("🟡 Processing video...")
        elif st.session_state.processing_status == "completed":
            status_placeholder.success("✅ Processing completed!")
        elif st.session_state.processing_status == "error":
            status_placeholder.error("❌ Error occurred during processing")
        
        # Recent activity log
        st.subheader("📋 Activity Log")
        if 'activity_log' not in st.session_state:
            st.session_state.activity_log = []
        
        for activity in st.session_state.activity_log[-5:]:  # Show last 5 activities
            st.text(activity)

def process_video(uploaded_file, auto_caption, meme_mode, add_broll, whisper_model, caption_style):
    """Process the uploaded video with selected options"""
    try:
        st.session_state.processing_status = "processing"
        st.session_state.activity_log.append("🚀 Starting video processing...")
        st.rerun()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        # Initialize processor
        processor = st.session_state.processor
        
        # Load video
        st.session_state.activity_log.append("📁 Loading video file...")
        processor.load_video(temp_path)
        
        # Process based on options
        if auto_caption:
            st.session_state.activity_log.append("🎤 Extracting audio...")
            processor.extract_audio()
            
            st.session_state.activity_log.append(f"🤖 Transcribing with {whisper_model} model...")
            processor.transcribe_audio(model=whisper_model)
            
            st.session_state.activity_log.append("📝 Adding captions...")
            processor.add_captions(style=caption_style)
        
        if meme_mode:
            st.session_state.activity_log.append("😄 Applying meme effects...")
            processor.apply_meme_effects()
        
        if add_broll:
            st.session_state.activity_log.append("🎥 Analyzing content for B-roll...")
            # TODO: Implement B-roll functionality
            st.session_state.activity_log.append("⚠️ B-roll feature coming soon!")
        
        # Export final video
        st.session_state.activity_log.append("💾 Exporting final video...")
        output_path = processor.export_video()
        
        st.session_state.processing_status = "completed"
        st.session_state.activity_log.append(f"✅ Video exported to: {output_path}")
        
        # Provide download link
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Download Processed Video",
                data=file.read(),
                file_name=f"clipforge_processed_{uploaded_file.name}",
                mime="video/mp4"
            )
        
        # Cleanup
        os.unlink(temp_path)
        
    except Exception as e:
        st.session_state.processing_status = "error"
        st.session_state.activity_log.append(f"❌ Error: {str(e)}")
        logger.error(f"Video processing error: {e}")
        st.error(f"Processing failed: {str(e)}")

if __name__ == "__main__":
    main() 