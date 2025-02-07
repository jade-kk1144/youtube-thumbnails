import streamlit as st

def render_header():
    col1, col2, col3 = st.columns([3,6,3])
    
    with col2:
        st.title("YouTube Thumbnail Analysis")
        st.write("Analyze trends and patterns in YouTube thumbnails")