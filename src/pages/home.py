# pages/home.py
import streamlit as st
from components.analysis_panels import (
    render_color_analysis,
    render_face_detection,
    render_text_analysis
)
from utils.youtube import extract_video_id, get_thumbnail

def render():
    # URL input
    url = st.text_input("Enter YouTube URL:")
    
    if url:
        video_id = extract_video_id(url)
        if video_id:
            thumbnail = get_thumbnail(video_id)
            
            # Create tabs for different analyses
            tab1, tab2, tab3 = st.tabs(["Colors", "Faces", "Text"])
            
            with tab1:
                render_color_analysis(thumbnail)
            
            with tab2:
                render_face_detection(thumbnail)
                
            with tab3:
                render_text_analysis(thumbnail)
