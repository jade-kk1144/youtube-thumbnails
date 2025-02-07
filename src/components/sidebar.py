# src/components/sidebar.py
import streamlit as st
from datetime import datetime, timedelta

def show_sidebar():
    with st.sidebar:
        st.title("YouTube Thumbnail Analysis")
        
        # URL input
        url = st.text_input("Enter YouTube URL")
        
        # Time range selector
        # st.subheader("Time Range")
        # date_range = st.date_input(
            # "Select date range",
            # value=(datetime.now() - timedelta(days=7), datetime.now()),
            # max_value=datetime.now()
        # )
        # 
        # Analysis options
        st.subheader("Analysis Options")
        options = {
            'color_analysis': st.checkbox("Color Analysis", value=True),
            # 'face_detection': st.checkbox("Face Detection", value=True),
            'text_detection': st.checkbox("Text Detection", value=True),
            'composition': st.checkbox("Composition Analysis", value=True)
        }
        
        # Advanced settings in expander
        with st.expander("Advanced Settings"):
            settings = {
                'color_count': st.slider("Number of colors to analyze", 3, 10, 5),
                # 'min_face_confidence': st.slider("Face detection confidence", 0.0, 1.0, 0.5),
                'min_text_confidence': st.slider("Text detection confidence", 0, 100, 50)
            }
        
        return {
            'url': url,
            # 'date_range': date_range,
            'options': options,
            'settings': settings
        }