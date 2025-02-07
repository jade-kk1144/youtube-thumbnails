# components/analysis_panels.py
import streamlit as st
from utils.image_analysis import analyze_colors, detect_faces, detect_text

def render_color_analysis(image):
    st.subheader("Color Analysis")
    colors = analyze_colors(image)
    
    cols = st.columns(len(colors))
    for idx, (color, percentage) in enumerate(colors):
        with cols[idx]:
            st.markdown(
                f'<div style="background-color: rgb{tuple(color)}; '
                f'height: 50px; border-radius: 5px;"></div>',
                unsafe_allow_html=True
            )
            st.write(f"{percentage:.1%}")

def render_face_detection(image):
    st.subheader("Face Detection")
    face_locations = detect_faces(image)
    # Face detection visualization code here

def render_text_analysis(image):
    st.subheader("Text Analysis")
    text = detect_text(image)
    # Text analysis visualization code here